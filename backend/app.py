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

# Configure CORS: allow only http://localhost:3000 and support credentials.
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# ----------------------- User Model -----------------------
class User(db.Model):
    unique_id = db.Column(db.String(250), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(250), nullable=False)

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
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    pharmacy_expiration = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # drug info
    generic_name = db.Column(db.String(250), nullable=False)
    labeler_name = db.Column(db.String(250), nullable=False)
    brand_name = db.Column(db.String(250), nullable=False)
    dosage_form = db.Column(db.String(250), nullable=False)
    route = db.Column(db.String(250), nullable=False)
    active_ingredients = db.Column(db.String(250), nullable=False)
    product_type = db.Column(db.String(250), nullable=False)
    package_description = db.Column(db.String(250), nullable=False)
    pharm_class = db.Column(db.String(250), nullable=False)
    
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

with app.app_context():
    db.create_all()

# google login endpoint
@app.route("/google_login", methods=["POST"])
def test_google_login():
    # Mark the session as permanent inside the request context.
    session.permanent = True  
    data = request.get_json(force=True)
    # Expect data to include: id, email, name, role, and address.
    google_unique_id = data.get("id")
    email = data.get("email")
    name = data.get("name", "Unknown")
    role_input = data.get("role", "").lower()
    role = role_input if role_input in ["pharmacy", "non_profit"] else "non_profit"
    address = data.get("address", "No address provided")
    
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            unique_id=google_unique_id,
            email=email,
            name=name,
            role=role,
            address=address
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.name = name
        user.role = role
        user.address = address
        db.session.commit()
    
    # Store user info in session
    session["user"] = user.to_dict()
    # Store pharmacy info in session if user is a pharmacy
    if role == "pharmacy":
        session["pharmacy_name"] = name
        session["pharmacy_address"] = address
    
    return jsonify({
        "message": "Test Google login successful",
        "user": user.to_dict()
    })

# ----------  MEDICINE ENDPOINTS  ----------
@app.route("/medicines", methods=["GET"])
def list_medicines():
    return jsonify([m.to_dict() for m in Medicine.query.all()])

@app.route("/medicines/<string:product_ndc>", methods=["GET"])
def get_medicine(product_ndc):
    med = db.session.get(Medicine, product_ndc)
    if med is None:
        abort(404, description="Medicine not found")
    return jsonify(med.to_dict())

@app.route("/medicines", methods=["POST"])
def create_medicine():
    # Check if user is authenticated and is a pharmacy
    if "user" not in session:
        abort(401, description="User not authenticated")
    
    user = session["user"]
    if user["role"] != "pharmacy":
        abort(403, description="Only pharmacies can create medicines")
    
    data = request.get_json(force=True)
    try:
        # Use pharmacy info from session instead of request data
        pharmacy_name = session["pharmacy_name"]
        pharmacy_address = session["pharmacy_address"]
        quantity = int(data["quantity"].strip())
        price = Decimal(str(data["price"]))
        pharmacy_expiration = date.fromisoformat(data["pharmacy_expiration"])
        product_ndc = data["product_ndc"].strip()
    except (KeyError, ValueError) as exc:
        abort(400, description=f"Invalid payload: {exc}")

    ndc_info = get_drug_info_by_ndc(product_ndc)
    if ndc_info is None:
        abort(404, description="No open‑FDA record found for that NDC")

    # Create a unique ID by combining product_ndc and pharmacy address.
    unique_id = f"{product_ndc}_{pharmacy_address.lower().replace(' ', '_').replace(',', '').replace('.', '')}"

    # Helpers to flatten lists or nested structures into simple strings
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
        pharmacy_name = pharmacy_name,
        address = pharmacy_address,
        unique_id = unique_id,
        price = price,
        quantity = quantity,
        pharmacy_expiration = pharmacy_expiration,
        created_at = datetime.utcnow(),

        # drug columns (all come from open‑FDA)
        generic_name = ndc_info.get("generic_name"),
        labeler_name = ndc_info.get("labeler_name"),
        brand_name = ndc_info.get("brand_name"),
        dosage_form = ndc_info.get("dosage_form"),
        route = csv_or_none(ndc_info.get("route")),
        active_ingredients = active_ings(ndc_info.get("active_ingredients")),
        product_type = ndc_info.get("product_type"),
        package_description = first_pkg_desc(ndc_info.get("packaging")),
        pharm_class = csv_or_none(ndc_info.get("pharm_class")),
    )
    db.session.add(medicine)
    db.session.commit()
    return jsonify(medicine.to_dict()), 201

@app.route("/medicines/<string:product_ndc>", methods=["DELETE"])
def delete_medicine(product_ndc):
    med = Medicine.query.get_or_404(product_ndc)
    db.session.delete(med)
    db.session.commit()
    return "", 204

@app.route("/medicines/query", methods=["GET"])
def query_medicines():
    term = request.args.get("name", "").strip()
    if not term:
        abort(400, description="Query string ?name= is required")

    # Perform a case-insensitive exact match by converting both sides to lower case.
    matches = Medicine.query.filter(
        func.lower(Medicine.generic_name) == term.lower()
    ).all()

    return jsonify([m.to_dict() for m in matches])

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()   # This removes all session data
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
