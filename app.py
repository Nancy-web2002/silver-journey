from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random, string

app = Flask(__name__)

# ✅ Allow all origins — including localhost for testing
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# === DATABASE CONFIG ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shipments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === MODEL ===
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(20), unique=True, nullable=False)
    shipper_name = db.Column(db.String(120))
    shipper_address = db.Column(db.String(200))
    receiver_name = db.Column(db.String(120))
    receiver_address = db.Column(db.String(200))
    receiver_phone = db.Column(db.String(50))
    receiver_email = db.Column(db.String(120))
    origin = db.Column(db.String(120))
    destination = db.Column(db.String(120))
    carrier = db.Column(db.String(50))
    shipment_type = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    shipment_mode = db.Column(db.String(50))
    carrier_ref_no = db.Column(db.String(100))
    product = db.Column(db.String(200))
    qty = db.Column(db.Integer)
    payment_mode = db.Column(db.String(50))
    total_freight = db.Column(db.String(50))
    expected_delivery = db.Column(db.String(50))
    departure_time = db.Column(db.String(50))
    pickup_date = db.Column(db.String(50))
    pickup_time = db.Column(db.String(50))
    comments = db.Column(db.String(500))
    status = db.Column(db.String(50), default="On Hold")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.columns}

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    return response

# === ROUTES ===

@app.route("/")
def home():
    return jsonify({"message": "Stockbridge Express Backend Active"}), 200


# ✅ Create new shipment
@app.route("/create_shipment", methods=["POST"])
def create_shipment():
    data = request.get_json()

    # Generate random tracking code
    tracking_code = "AWB" + ''.join(random.choices(string.digits, k=12))

    new_shipment = Shipment(
        tracking_code=tracking_code,
        shipper_name=data.get("shipper_name"),
        shipper_address=data.get("shipper_address"),
        receiver_name=data.get("receiver_name"),
        receiver_address=data.get("receiver_address"),
        receiver_phone=data.get("receiver_phone"),
        receiver_email=data.get("receiver_email"),
        origin=data.get("origin"),
        destination=data.get("destination"),
        carrier=data.get("carrier"),
        shipment_type=data.get("shipment_type"),
        weight=data.get("weight"),
        shipment_mode=data.get("shipment_mode"),
        carrier_ref_no=data.get("carrier_ref_no"),
        product=data.get("product"),
        qty=data.get("qty"),
        payment_mode=data.get("payment_mode"),
        total_freight=data.get("total_freight"),
        expected_delivery=data.get("expected_delivery"),
        departure_time=data.get("departure_time"),
        pickup_date=data.get("pickup_date"),
        pickup_time=data.get("pickup_time"),
        comments=data.get("comments"),
        status=data.get("status", "On Hold")
    )

    db.session.add(new_shipment)
    db.session.commit()

    return jsonify({
        "message": "Shipment created successfully",
        "tracking_code": tracking_code
    }), 200


# ✅ Handle browser CORS preflight requests (OPTIONS)
@app.route("/create_shipment", methods=["OPTIONS"])
def shipment_options():
    reponse = jsonify({"status": "OK"})
    reponse.headers.add("Access-Control-Allow-Origin", "*")
    reponse.headers.add("Access-Control-Allow-Headers", "Content-Type")
    reponse.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return reponse, 200


# ✅ Track shipment by tracking code
@app.route("/track_shipment/<tracking_code>", methods=["GET"])
def track_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404
    return jsonify({"shipment": shipment.to_dict()}), 200


# ✅ Update shipment status or details (Admin)
@app.route("/update_shipment/<tracking_code>", methods=["PUT"])
def update_shipment(tracking_code):
    data = request.get_json()
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404

    for key, value in data.items():
        if hasattr(shipment, key):
            setattr(shipment, key, value)

    db.session.commit()
    return jsonify({"message": "Shipment updated successfully"}), 200


# === INITIALIZE DATABASE ===
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)