from datetime import datetime, date
import json
from decimal import Decimal

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.dialects.sqlite import JSON  # works on SQLite ≥3.38
# If your SQLite is older, store JSON as Text and json.dumps/loads manually.

from ndc_service import get_drug_info_by_ndc   # <- the helper above

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Marketplace.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

CORS(app)

# ----------  NEW MODEL  ----------
class Medicine(db.Model):
    # pharamacy info
    product_ndc = db.Column(db.String(20), primary_key=True)
    pharmacy_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250), nullable=False)  # <-- new field
    pharmacy_id = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    pharmacy_expiration = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #drug info
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
            "pharmacy_id":          self.pharmacy_id,
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
        pharmacy_id = data["pharmacy_id"].strip()
        created_at = datetime.utcnow()
    except (KeyError, ValueError) as exc:
        abort(400, description=f"Invalid payload: {exc}")

    ndc_info = get_drug_info_by_ndc(product_ndc)
    if ndc_info is None:
        abort(404, description="No open‑FDA record found for that NDC")

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
        pharmacy_id = pharmacy_id,
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

if __name__ == "__main__":
    app.run(debug=True)
