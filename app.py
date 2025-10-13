from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random, string

app = Flask(__name__)

# === CORS SETUP (Allow both local and deployed frontends) ===
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5501", "https://stockbridge-0c44.onrender.com"]}})

# === DATABASE CONFIG ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shipments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === MODELS ===
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(100), unique=True, nullable=False)
    shipper_name = db.Column(db.String(100))
    receiver_name = db.Column(db.String(100))
    status = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    carrier = db.Column(db.String(100))
    expected_delivery = db.Column(db.String(100))
    history = db.relationship('ShipmentHistory', backref='shipment', lazy=True, cascade="all, delete-orphan", order_by="desc(ShipmentHistory.id)")

    def to_dict(self):
        return {
            "tracking_code": self.tracking_code,
            "status": self.status,
            "origin": self.origin,
            "destination": self.destination,
            "carrier": self.carrier,
            "expected_delivery": self.expected_delivery,
            "history": [h.to_dict() for h in self.history]  # ✅ FIXED
        }


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

# === GLOBAL CORS HEADERS ===
@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


# === ROUTES ===

@app.route("/")
def home():
    return jsonify({"message": "Stockbridge Express Backend Active"}), 200


# ✅ CREATE NEW SHIPMENT
@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.get_json()

    tracking_code = "AWB" + ''.join(random.choices(string.digits, k=12))

    new_shipment = Shipment(
        tracking_code=tracking_code,
        shipper_name=data.get("shipper_name"),
        receiver_name=data.get("receiver_name"),
        status=data.get("status", "Pending"),
        origin=data.get("origin"),
        destination=data.get("destination"),
        carrier=data.get("carrier"),
        expected_delivery=data.get("expected_delivery")
    )

    db.session.add(new_shipment)
    db.session.commit()

    # Add initial shipment history
    now = datetime.now()
    first_history = ShipmentHistory(
        shipment_id=new_shipment.id,
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%I:%M %p"),
        location=data.get("origin", "Origin"),
        status=data.get("status", "Pending"),
        updated_by="Admin",
        remarks="Shipment created"
    )
    db.session.add(first_history)
    db.session.commit()

    return jsonify({
        "message": "Shipment created successfully",
        "tracking_code": tracking_code
    }), 201


# ✅ TRACK SHIPMENT
@app.route("/track_shipment/<tracking_code>", methods=["GET"])
def track_shipment(tracking_code):
    try:
        shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
        if not shipment:
            return jsonify({"message": "Shipment not found"}), 404

        return jsonify(shipment.to_dict()), 200

    except Exception as e:
        print(f"Error tracking shipment: {e}")
        return jsonify({"message": "Server error"}), 500


# ✅ UPDATE SHIPMENT
@app.route('/update_shipment/<tracking_code>', methods=['POST'])
def update_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404

    data = request.get_json()
    new_location = data.get("location")
    new_status = data.get("status")
    updated_by = data.get("updated_by", "Admin")
    remarks = data.get("remarks", "")

    date_value = data.get ("date") or datetime.now() .strftime("%Y-%m-%d")
    time_value = data.get("time") or datetime.now() .strftime("%Y-%m-%d")
    shipment.status = new_status

    now = datetime.now()
    new_history = ShipmentHistory(
        shipment_id=shipment.id,
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%I:%M %p"),
        location=new_location,
        status=new_status,
        updated_by=updated_by,
        remarks=remarks
    )
    db.session.add(new_history)
    db.session.commit()

    return jsonify({"message": "Shipment updated successfully"}), 200


# ✅ DEBUG ROUTE (optional)
@app.route('/debug_history/<tracking_code>')
def debug_history(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404

    histories = ShipmentHistory.query.filter_by(shipment_id=shipment.id).all()
    return jsonify({
        "shipment_id": shipment.id,
        "history_count": len(histories),
        "history_records": [h.to_dict() for h in histories]
    })


# === INITIALIZE DATABASE ===
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)