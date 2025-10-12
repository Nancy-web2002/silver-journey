from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random, string

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# === DATABASE CONFIG ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shipments.db'  # use SQLite for local; PostgreSQL for Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === MODELS ===

class ShipmentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipment.id'), nullable=False)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    location = db.Column(db.String(100))
    status = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))
    remarks = db.Column(db.String(200))

    def to_dict(self):
        return {
            "date": self.date,
            "time": self.time,
            "location": self.location,
            "status": self.status,
            "updated_by": self.updated_by,
            "remarks": self.remarks
        }

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(100), unique=True, nullable=False)
    shipper_name = db.Column(db.String(100))
    shipper_address = db.Column(db.String(200))
    receiver_name = db.Column(db.String(100))
    receiver_address = db.Column(db.String(200))
    receiver_phone = db.Column(db.String(50))
    receiver_email = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    carrier = db.Column(db.String(50))
    shipment_type = db.Column(db.String(50))
    product = db.Column(db.String(100))
    weight = db.Column(db.String(50))
    payment_mode = db.Column(db.String(50))
    total_freight = db.Column(db.String(50))
    expected_delivery = db.Column(db.String(50))
    departure_time = db.Column(db.String(50))
    pickup_date = db.Column(db.String(50))
    pickup_time = db.Column(db.String(50))
    status = db.Column(db.String(50))
    comments = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    history = db.relationship('ShipmentHistory', backref='shipment', lazy=True)

    def to_dict(self):
        return {
            "tracking_code": self.tracking_code,
            "shipper_name": self.shipper_name,
            "shipper_address": self.shipper_address,
            "receiver_name": self.receiver_name,
            "receiver_address": self.receiver_address,
            "receiver_phone": self.receiver_phone,
            "receiver_email": self.receiver_email,
            "origin": self.origin,
            "destination": self.destination,
            "carrier": self.carrier,
            "shipment_type": self.shipment_type,
            "product": self.product,
            "weight": self.weight,
            "payment_mode": self.payment_mode,
            "total_freight": self.total_freight,
            "expected_delivery": self.expected_delivery,
            "departure_time": self.departure_time,
            "pickup_date": self.pickup_date,
            "pickup_time": self.pickup_time,
            "status": self.status,
            "comments": self.comments,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "history": [h.to_dict() for h in self.history]  # ✅ include history
        }

# === ROUTES ===
@app.route('/')
def home():
    return jsonify({"message": "Stockbridge backend running successfully!"})

@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.get_json() or {}
    tracking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

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
        product=data.get("product"),
        weight=data.get("weight"),
        payment_mode=data.get("payment_mode"),
        total_freight=data.get("total_freight"),
        expected_delivery=data.get("expected_delivery"),
        departure_time=data.get("departure_time"),
        pickup_date=data.get("pickup_date"),
        pickup_time=data.get("pickup_time"),
        status=data.get("status"),
        comments=data.get("comments")
    )

    db.session.add(new_shipment)
    db.session.commit()

    return jsonify({"message": "Shipment created successfully!", "tracking_code": tracking_code}), 201


@app.route('/track_shipment/<tracking_code>', methods=['GET'])
def track_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404
    return jsonify(shipment.to_dict()), 200


@app.route('/update_shipment/<tracking_code>', methods=['POST'])
def update_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404

    data = request.get_json() or {}

    new_history = ShipmentHistory(
        shipment_id=shipment.id,
        date=data.get("date"),
        time=data.get("time"),
        location=data.get("location"),
        status=data.get("status"),
        updated_by=data.get("updated_by"),
        remarks=data.get("remarks")
    )

    shipment.status = data.get("status", shipment.status)

    db.session.add(new_history)
    db.session.commit()

    return jsonify({"message": "Shipment updated successfully!"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)