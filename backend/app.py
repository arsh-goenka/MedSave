from datetime import datetime, date, timedelta
import json
from decimal import Decimal
import os

from flask import Flask, jsonify, request, abort, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.dialects.sqlite import JSON  # works on SQLite ≥3.38
from sqlalchemy import func

# Import Flask-Dance for Google OAuth
from flask_dance.contrib.google import make_google_blueprint, google

from ndc_service import get_drug_info_by_ndc  # <- the helper above

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Marketplace.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Set a secret key; in production, set this as an environment variable.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # adjust lifetime as needed
db = SQLAlchemy(app)

# Configure CORS with specific settings
CORS(app,
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Pharmacy-Credentials"],
         "supports_credentials": True
     }})

with app.app_context():
    db.drop_all()  # Clears the existing database tables
    db.create_all()  # Creates tables based on your current models

# ----------------------- User Model -----------------------
class User(db.Model):
    unique_id = db.Column(db.String(250), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            "unique_id": self.unique_id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "address": self.address,
        }

# ----------------------- Medicine Model -----------------------
class Medicine(db.Model):
    # pharmacy info
    product_ndc = db.Column(db.String(20), nullable=False)
    pharmacy_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250), nullable=False)  # <-- new field

    unique_id = db.Column(db.String(250), primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    pharmacy_expiration = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #drug info
    generic_name = db.Column(db.String(250), nullable=True)
    labeler_name = db.Column(db.String(250), nullable=True)
    brand_name = db.Column(db.String(250), nullable=True)
    dosage_form = db.Column(db.String(250), nullable=True)
    route = db.Column(db.String(250), nullable=True)
    active_ingredients = db.Column(db.String(250), nullable=True)
    product_type = db.Column(db.String(250), nullable=True)
    package_description = db.Column(db.String(250), nullable=True)
    pharm_class = db.Column(db.String(250), nullable=True)
    
    def to_dict(self):
        return {
            # pharmacy info
            "product_ndc":          self.product_ndc,
            "pharmacy_name":        self.pharmacy_name,
            "address":              self.address,
            "unique_id":            self.unique_id,
            "price":                str(self.price),
            "quantity":             self.quantity,
            "pharmacy_expiration":  self.pharmacy_expiration.isoformat(),
            "created_at":           self.created_at.isoformat(),

            # drug info
            "generic_name":         self.generic_name,
            "labeler_name":         self.labeler_name,
            "brand_name":           self.brand_name,
            "dosage_form":          self.dosage_form,
            "route":                self.route,
            "active_ingredients":   self.active_ingredients,
            "product_type":         self.product_type,
            "package_description":  self.package_description,
            "pharm_class":          self.pharm_class,
        }

# backend/app.py

# ... (imports and model definitions) ...

with app.app_context():
    db.create_all()

# google login endpoint
@app.route("/google_login", methods=["POST"])
def test_google_login():

    session.permanent = True

    # The OPTIONS check should typically be handled by Flask-CORS automatically
    # if configured correctly. You might not need this explicit check.
    # if request.method == "OPTIONS":
    #     # Handle CORS preflight request
    #     return jsonify({"message": "CORS preflight check successful"}), 200

    try:
        data = request.get_json(force=True)
        print("Received data for login:", data) # Log login data

        # ... (validation logic remains the same) ...
        google_unique_id = data.get("unique_id")
        # ... other validations ...

        email = data.get("email")
        name = data.get("name")
        role = data.get("role")
        address = data.get("address")

        if not all([google_unique_id, email, name, role, address]):
             abort(400, description="Missing one or more required fields: unique_id, email, name, role, address")

        # Fetch user by unique_id (Google's sub is usually the unique ID)
        user = User.query.filter_by(unique_id=google_unique_id).first()

        if user is None:
            # Check if email exists for another user (edge case)
            existing_email_user = User.query.filter_by(email=email).first()
            if existing_email_user:
                # Handle scenario where email is already taken but unique_id is different
                # This might indicate an issue or require a specific resolution strategy
                 abort(409, description="Email already associated with a different account.")

            # Create a new user if not found
            user = User(
                unique_id=google_unique_id,
                email=email,
                name=name,
                role=role,
                address=address,
            )
            db.session.add(user)
            print(f"Creating new user: {user.to_dict()}")
        else:
            # Update existing user if needed (e.g., name/address might change)
            # Decide on your update strategy here. For now, let's update all fields
            # except unique_id and potentially email if you want it fixed.
            user.name = name
            user.role = role
            user.address = address
            # Optionally update email if it can change: user.email = email
            print(f"Updating existing user: {user.to_dict()}")

        db.session.commit()
        print("User successfully added/updated in the database.")

        # ***** CRITICAL FIX: Store user info in the session *****
        session["user"] = user.to_dict()
        print(f"Session set: {session['user']}") # Log session data

        return jsonify({"message": "User successfully authenticated", "user": user.to_dict()})

    except Exception as e:
        db.session.rollback() # Ensure rollback on any error during processing
        print(f"Error in /google_login: {e}")
        # Be careful about exposing internal errors directly in production
        # Use a generic error message unless specifically debugging
        abort(500, description=f"Internal Server Error: {e}")


# ... (rest of your User and Medicine models) ...

# ----------  MEDICINE ENDPOINTS  ----------
@app.route("/medicines", methods=["GET"])
def list_medicines():
    # Potentially add auth check here if only logged-in users can view
    # if "user" not in session:
    #    abort(401, description="User not authenticated")
    return jsonify([m.to_dict() for m in Medicine.query.all()])

@app.route("/medicines/<string:unique_id>", methods=["GET"]) # Use unique_id
def get_medicine(unique_id):
    # Potentially add auth check here
    # if "user" not in session:
    #    abort(401, description="User not authenticated")
    med = db.session.get(Medicine, unique_id) # Use the correct primary key
    if med is None:
        abort(404, description="Medicine not found")
    return jsonify(med.to_dict())

@app.route("/medicines", methods=["POST"])
def create_medicine():
    print(f"Checking session before creating medicine: {session.get('user')}") # Log session content
    # Check if user is authenticated and is a pharmacy
    if "user" not in session:
        abort(401, description="User not authenticated")

    user_data = session["user"] # Get user data from session
    print(f"User data from session: {user_data}") # Log user data

    if user_data.get("role") != "pharmacy":
        abort(403, description="Only pharmacies can create medicines")

    data = request.get_json(force=True)
    print(f"Received data for creating medicine: {data}") # Log medicine data
    try:
        # ***** FIX: Use pharmacy info from session *****
        pharmacy_name = user_data["name"]       # Use name from the logged-in user session
        pharmacy_address = user_data["address"] # Use address from the logged-in user session

        quantity = int(data["quantity"].strip())
        price = Decimal(str(data["price"]))
        pharmacy_expiration = date.fromisoformat(data["pharmacy_expiration"])
        product_ndc = data["product_ndc"].strip()

    except (KeyError, ValueError, TypeError) as exc:
        print(f"Payload error: {exc}, Data: {data}")
        abort(400, description=f"Invalid or missing payload field: {exc}")
    except Exception as e:
        print(f"Unexpected error during data extraction: {e}")
        abort(500, description="Internal server error during data processing")


    print(f"Attempting to fetch NDC info for: {product_ndc}")
    ndc_info = get_drug_info_by_ndc(product_ndc)
    if ndc_info is None:
        print(f"NDC info not found for {product_ndc}")
        abort(404, description="No open‑FDA record found for that NDC")
    print(f"NDC info found: {ndc_info.get('generic_name', 'N/A')}")

    # Create a unique ID by combining product_ndc and pharmacy address.
    # Ensure address is consistently formatted (lowercase, no extra spaces)
    clean_address = "_".join(pharmacy_address.lower().split()) # Basic cleaning
    unique_id = f"{product_ndc}_{clean_address}"
    print(f"Generated unique_id: {unique_id}")

    # Check if medicine with this unique_id already exists
    existing_medicine = db.session.get(Medicine, unique_id)
    if existing_medicine:
        print(f"Medicine with unique_id {unique_id} already exists.")
        # Decide how to handle duplicates: update? reject?
        # For now, let's reject with a 409 Conflict
        abort(409, description=f"Medicine listing for NDC {product_ndc} at this address already exists.")


    # ... (helper functions csv_or_none, active_ings, first_pkg_desc) ...
    def csv_or_none(seq: list[str] | None) -> str | None:
         return ", ".join(seq) if seq else None

    def active_ings(ings: list[dict] | None) -> str | None:
         if not ings:
             return None
         return ", ".join(f"{i['name']} {i['strength']}" for i in ings)

    def first_pkg_desc(pkgs: list[dict] | None) -> str | None:
         return pkgs[0]["description"] if pkgs else None


    medicine = Medicine(
        product_ndc = product_ndc,
        pharmacy_name = pharmacy_name,      # From session
        address = pharmacy_address,         # From session
        unique_id = unique_id,              # Generated unique ID
        price = price,
        quantity = quantity,
        pharmacy_expiration = pharmacy_expiration,
        created_at = datetime.utcnow(),

        # drug columns (all come from open‑FDA)
        generic_name=ndc_info.get("generic_name"),
        labeler_name=ndc_info.get("labeler_name"),
        brand_name=ndc_info.get("brand_name"),
        dosage_form=ndc_info.get("dosage_form"),
        route=csv_or_none(ndc_info.get("route")),
        active_ingredients=active_ings(ndc_info.get("active_ingredients")),
        product_type=ndc_info.get("product_type"),
        package_description=first_pkg_desc(ndc_info.get("packaging")),
        pharm_class=csv_or_none(ndc_info.get("pharm_class")),
    )

    try:
        db.session.add(medicine)
        db.session.commit()
        print(f"Medicine successfully added: {medicine.to_dict()}")
        return jsonify(medicine.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Database error adding medicine: {e}")
        abort(500, description="Internal Server Error: Could not save medicine to database.")


# Change parameter and lookup logic to use unique_id
@app.route("/medicines/<string:unique_id>", methods=["DELETE"])
def delete_medicine(unique_id):
    # Add authentication check here - maybe only the pharmacy that added it?
    # if "user" not in session:
    #    abort(401, description="User not authenticated")
    med = db.session.get(Medicine, unique_id)
    if med is None:
         abort(404, description="Medicine not found")

    # Optional: Check if the logged-in user is allowed to delete this
    # user_data = session['user']
    # if user_data['role'] != 'pharmacy' or med.address != user_data['address']:
    #     abort(403, description="Forbidden: You cannot delete this medicine listing.")

    db.session.delete(med)
    db.session.commit()
    print(f"Medicine with unique_id {unique_id} deleted.")
    return "", 204

@app.route("/medicines/query", methods=["GET"])
def query_medicines():
    # Add auth check?
    # if "user" not in session:
    #    abort(401, description="User not authenticated")
    term = request.args.get("name", "").strip()
    if not term:
        abort(400, description="Query string ?name= is required")

    # Perform a case-insensitive search using `ilike` for partial matches
    # Or use exact match as before if required
    matches = Medicine.query.filter(
        # func.lower(Medicine.generic_name) == term.lower() # Exact match
         Medicine.generic_name.ilike(f"%{term}%") # Partial match
    ).all()

    return jsonify([m.to_dict() for m in matches])

@app.route('/logout', methods=['POST'])
def logout():
    user_email = session.get('user', {}).get('email', 'Unknown User')
    session.clear()   # This removes all session data
    print(f"User {user_email} logged out.")
    return jsonify({"message": "Logged out successfully"}), 200


# ... (rest of the file, including __main__ block) ...

if __name__ == "__main__":
    app.run(debug=True) # debug=True helps see logs and errors
