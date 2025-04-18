from datetime import datetime, date
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
db = SQLAlchemy(app)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow frontend origin

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
    # pharamacy info
    product_ndc = db.Column(db.String(20), nullable=True)
    pharmacy_name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(250), nullable=True)  # <-- new field
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
            "unique_id":           self.unique_id,
            "price":                str(self.price),
            "quantity":             self.quantity,                 # typo fixed
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
@app.route("/google_login", methods=["POST", "OPTIONS"])
def test_google_login():
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        return jsonify({"message": "CORS preflight check successful"}), 200

    try:
        data = request.get_json(force=True)
        print("Received data:", data)  # Log the received data for debugging

        # Validate required fields
        google_unique_id = data.get("unique_id")
        if not google_unique_id:
            abort(400, description="Missing required field: unique_id in the request payload")

        email = data.get("email")
        if not email:
            abort(400, description="Missing required field: email in the request payload")

        name = data.get("name")
        if not name:
            abort(400, description="Missing required field: name in the request payload")

        role = data.get("role")
        if not role:
            abort(400, description="Missing required field: role in the request payload")

        address = data.get("address")
        if not address:
            abort(400, description="Missing required field: address in the request payload")

        # Fetch user by email
        user = User.query.filter_by(email=email).first()
        if user is None:
            # Create a new user if not found
            user = User(
                unique_id=google_unique_id,
                email=email,
                name=name,
                role=role,
                address=address,
            )
            db.session.add(user)
        else:
            # Only update the unique_id, keep other fields intact
            user.unique_id = google_unique_id

        try:
            db.session.commit()
            print("User successfully added/updated in the database.")
            return jsonify({"message": "User successfully authenticated", "user": user.to_dict()})
        except Exception as e:
            print(f"Database error: {e}")
            db.session.rollback()
            abort(500, description="Internal Server Error: Could not update user in the database.")
    except Exception as e:
        print(f"Error in /google_login: {e}")
        abort(500, description="Internal Server Error: An unexpected error occurred")

# ----------  MEDICINE ENDPOINTS  ----------
@app.route("/medicines", methods=["GET"])
def list_medicines():
    return jsonify([m.to_dict() for m in Medicine.query.all()])

@app.route("/medicines/<string:product_ndc>", methods=["GET"])
def get_medicine(product_ndc):
    print("first")
    med = db.session.get(Medicine, product_ndc)
    print("second")
    if med is None:
        abort(404, description="Medicine not found")
    return jsonify(med.to_dict())

@app.route("/medicines", methods=["POST"])
def create_medicine():
    data = request.get_json(force=True)
    try:
        pharmacy_name = data["pharmacy_name"].strip()
        quantity = int(data["quantity"].strip())
        address = data["address"].strip()  
        price = Decimal(str(data["price"]))
        pharmacy_expiration = date.fromisoformat(data["pharmacy_expiration"])
        product_ndc = data["product_ndc"].strip()
        created_at = datetime.utcnow()
    except (KeyError, ValueError) as exc:
        abort(400, description=f"Invalid payload: {exc}")

    ndc_info = get_drug_info_by_ndc(product_ndc)
    if ndc_info is None:
        abort(404, description="No open‑FDA record found for that NDC")

    # Create a unique ID by combining product_ndc and pharmacy address
    # Remove spaces and special characters to ensure consistency
    unique_id = f"{product_ndc}_{address.lower().replace(' ', '_').replace(',', '').replace('.', '')}"

    # Helpers to flatten lists or nested structures into simple strings
    def csv_or_none(seq: list[str] | None) -> str | None:
        return ", ".join(seq) if seq else None

    def active_ings(ings: list[dict] | None) -> str | None:
        if not ings:
            return None
        return ", ".join(f"{i['name']} {i['strength']}" for i in ings)

    def first_pkg_desc(pkgs: list[dict] | None) -> str | None:
        return pkgs[0]["description"] if pkgs else None

    if ndc_info is None:
        abort(404, description="No open‑FDA record found for that NDC")

    medicine = Medicine(
        product_ndc = product_ndc,
        pharmacy_name = pharmacy_name,
        address = address,
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
def delete_medicine(med_id):
    med = Medicine.query.get_or_404(med_id)
    db.session.delete(med)
    db.session.commit()
    return "", 204

@app.route("/medicines/query")
def query_medicines():

    term = request.args.get("name", "").strip()
    if not term:
        abort(400, description="Query string ?name= is required")

    # Perform a case-insensitive exact match by converting both sides to lower case.
    matches = Medicine.query.filter(
        func.lower(Medicine.generic_name) == term.lower()
    ).all()

    return jsonify([m.to_dict() for m in matches])

if __name__ == "__main__":
    app.run(debug=True)
