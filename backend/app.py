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
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos2.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

CORS(app)

# ----------  EXISTING MODEL  ----------
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }

# ----------  NEW MODEL  ----------
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_name = db.Column(db.String(120), nullable=False)
    pharmacy_address = db.Column(db.String(250), nullable=False)  # <-- new field
    price = db.Column(db.Numeric(10, 2), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    ndc_code = db.Column(db.String(30), nullable=False, unique=True)
    ndc_info = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pharmacy_name": self.pharmacy_name,
            "pharmacy_address": self.pharmacy_address,
            "price": str(self.price),
            "expiry_date": self.expiry_date.isoformat(),
            "ndc_code": self.ndc_code,
            "ndc_info": self.ndc_info,
            "created_at": self.created_at.isoformat(),
        }

with app.app_context():
    db.create_all()

# ----------  TODO ENDPOINTS (unchanged)  ----------
@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify([t.to_dict() for t in Todo.query.all()])

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json(force=True)
    new_todo = Todo(task=data["task"])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json(force=True)
    todo = Todo.query.get_or_404(todo_id)
    todo.task = data.get("task", todo.task)
    todo.completed = data.get("completed", todo.completed)
    db.session.commit()
    return jsonify(todo.to_dict())

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return "", 204

# ----------  MEDICINE ENDPOINTS  ----------
@app.route("/medicines", methods=["GET"])
def list_medicines():
    return jsonify([m.to_dict() for m in Medicine.query.all()])

@app.route("/medicines", methods=["POST"])
def create_medicine():
    data = request.get_json(force=True)
    try:
        pharmacy_name = data["pharmacy_name"].strip()
        pharmacy_address = data["pharmacy_address"].strip()  # <-- new
        price = Decimal(str(data["price"]))
        expiry_date = date.fromisoformat(data["expiry_date"])
        ndc_code = data["ndc_code"].strip()
    except (KeyError, ValueError) as exc:
        abort(400, description=f"Invalid payload: {exc}")

    ndc_info = get_drug_info_by_ndc(ndc_code)
    if ndc_info is None:
        abort(404, description="No open‑FDA record found for that NDC")

    medicine = Medicine(
        pharmacy_name=pharmacy_name,
        pharmacy_address=pharmacy_address,  # <-- new
        price=price,
        expiry_date=expiry_date,
        ndc_code=ndc_code,
        ndc_info=ndc_info,
    )
    db.session.add(medicine)
    db.session.commit()
    return jsonify(medicine.to_dict()), 201

@app.route("/medicines/<int:med_id>", methods=["DELETE"])
def delete_medicine(med_id):
    med = Medicine.query.get_or_404(med_id)
    db.session.delete(med)
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
