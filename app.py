from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random, string

app = Flask(__name__)

# Allow local testing and deployed frontend
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5501", "https://stockbridge-0c44.onrender.com"]}})

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shipments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS (expanded to include fields your frontend expects)
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(100), unique=True, nullable=False)

    # sender / receiver
    shipper_name = db.Column(db.String(200))
    shipper_address = db.Column(db.String(300))
    receiver_name = db.Column(db.String(200))
    receiver_address = db.Column(db.String(300))
    receiver_phone = db.Column(db.String(100))
    receiver_email = db.Column(db.String(200))

    # shipment details
    status = db.Column(db.String(100))
    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    carrier = db.Column(db.String(200))
    type_of_shipment = db.Column(db.String(200))
    weight = db.Column(db.String(100))
    shipment_mode = db.Column(db.String(100))
    carrier_reference_no = db.Column(db.String(200))
    product = db.Column(db.String(200))
    quantity = db.Column(db.String(50))
    payment_mode = db.Column(db.String(100))
    total_freight = db.Column(db.String(100))
    expected_delivery = db.Column(db.String(100))
    departure_time = db.Column(db.String(100))
    pickup_date = db.Column(db.String(100))
    pickup_time = db.Column(db.String(100))
    comments = db.Column(db.String(500))

    history = db.relationship(
        'ShipmentHistory',
        backref='shipment',
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(ShipmentHistory.id)"
    )

    def to_dict(self):
        return {
            "tracking_code": self.tracking_code,
            "shipper_name": self.shipper_name,
            "shipper_address": self.shipper_address,
            "receiver_name": self.receiver_name,
            "receiver_address": self.receiver_address,
            "receiver_phone": self.receiver_phone,
            "receiver_email": self.receiver_email,
            "status": self.status,
            "origin": self.origin,
            "destination": self.destination,
            "carrier": self.carrier,
            "type_of_shipment": self.type_of_shipment,
            "weight": self.weight,
            "shipment_mode": self.shipment_mode,
            "carrier_reference_no": self.carrier_reference_no,
            "product": self.product,
            "quantity": self.quantity,
            "payment_mode": self.payment_mode,
            "total_freight": self.total_freight,
            "expected_delivery": self.expected_delivery,
            "departure_time": self.departure_time,
            "pickup_date": self.pickup_date,
            "pickup_time": self.pickup_time,
            "comments": self.comments,
            "history": [h.to_dict() for h in self.history]
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

# GLOBAL CORS HEADERS (keeps simple)
@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
    return response

# ROUTES
@app.route("/")
def home():
    return jsonify({"message": "Stockbridge Express Backend Active"}), 200

# CREATE NEW SHIPMENT (accepts all fields)
@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.get_json() or {}

    tracking_code = "AWB" + ''.join(random.choices(string.digits, k=12))

    new_shipment = Shipment(
        tracking_code=tracking_code,
        shipper_name=data.get("shipper_name"),
        shipper_address=data.get("shipper_address"),
        receiver_name=data.get("receiver_name"),
        receiver_address=data.get("receiver_address"),
        receiver_phone=data.get("receiver_phone"),
        receiver_email=data.get("receiver_email"),
        status=data.get("status", "Pending"),
        origin=data.get("origin"),
        destination=data.get("destination"),
        carrier=data.get("carrier"),
        type_of_shipment=data.get("type_of_shipment"),
        weight=data.get("weight"),
        shipment_mode=data.get("shipment_mode"),
        carrier_reference_no=data.get("carrier_reference_no"),
        product=data.get("product"),
        quantity=data.get("quantity"),
        payment_mode=data.get("payment_mode"),
        total_freight=data.get("total_freight"),
        expected_delivery=data.get("expected_delivery"),
        departure_time=data.get("departure_time"),
        pickup_date=data.get("pickup_date"),
        pickup_time=data.get("pickup_time"),
        comments=data.get("comments")
    )

    db.session.add(new_shipment)
    db.session.commit()

    # Optionally add the first history entry
    now = datetime.now()
    first_history = ShipmentHistory(
        shipment_id=new_shipment.id,
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%I:%M %p"),
        location=new_shipment.origin or "Origin",
        status=new_shipment.status or "Pending",
        updated_by="Admin",
        remarks="Shipment created"
    )
    db.session.add(first_history)
    db.session.commit()

    return jsonify({"message": "Shipment created successfully", "tracking_code": tracking_code}), 201

# TRACK SHIPMENT
@app.route("/track_shipment/<tracking_code>", methods=["GET"])
def track_shipment(tracking_code):
    try:
        shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
        if not shipment:
            return jsonify({"message": "Shipment not found"}), 404

        # Return full dict (to_dict handles history)
        return jsonify(shipment.to_dict()), 200

    except Exception as e:
        # Server-side log — check your logs if errors occur
        print(f"Error tracking shipment: {e}")
        return jsonify({"message": "Server error"}), 500
        

# UPDATE SHIPMENT
@app.route('/update_shipment/<tracking_code>', methods=['POST'])
def update_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"message": "Shipment not found"}), 404

    data = request.get_json() or {}
    new_location = data.get("location", "Unknown Location")
    new_status = data.get("status", shipment.status or "Pending")
    updated_by = data.get("updated_by", "Admin")
    remarks = data.get("remarks", "Status updated")

    date_value = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    time_value = data.get("time") or datetime.now().strftime("%I:%M %p")

    print(f"🟢 Updating {tracking_code}: {new_status} at {new_location}")

    # Update main shipment status
    shipment.status = new_status

    # Add new history record
    new_history = ShipmentHistory.id(
        shipment_id=shipment.id,
        date=date_value,
        time=time_value,
        location=new_location,
        status=new_status,
        updated_by=updated_by,
        remarks=remarks
    )
    db.session.add(new_history)
    db.session.commit()

    return jsonify({"message": "Shipment updated successfully"}), 200
# DEBUG: list history for a shipment
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

# OPTIONAL: add a sample shipment for testing (uncomment to use)
@app.route('/add_sample_shipment')
def add_sample_shipment():
    sample = Shipment(
    tracking_code="AWB824373517914",
     shipper_name="John Smith",
     shipper_address="123 Warehouse Rd, London",
     receiver_name="Maria Rossi",
       receiver_address="45 Via Roma, Milan",
      receiver_phone="+39 334 567 8910",
       receiver_email="maria@example.com",
       status="In Transit",
       origin="London, UK",
        destination="Milan, Italy",
        carrier="StockBridge Express",
        type_of_shipment="Air Freight",
        weight="23kg",
       shipment_mode="Air",
      carrier_reference_no="REF123456",
        product="Electronics",
       quantity="2",
        payment_mode="Prepaid",
        total_freight="$150",
      expected_delivery="2025-10-15",
        departure_time="10:00 AM",
        pickup_date="2025-10-10",
        pickup_time="9:00 AM",
        comments="Package cleared customs"
   )
    db.session.add(sample)
    db.session.commit()
    return jsonify({"message":"sample added"})

# INITIALIZE DB
with app.app_context():
    db.create_all()

    # Create or get sample shipment
    shipment = Shipment.query.filter_by(tracking_code="AWB824373517914").first()
    if not shipment:
        shipment = Shipment(
            tracking_code="AWB824373517914",
            shipper_name="John Smith",
            shipper_address="123 Warehouse Rd, London",
            receiver_name="Maria Rossi",
            receiver_address="45 Via Roma, Milan",
            receiver_phone="+39 334 567 8910",
            receiver_email="maria@example.com",
            status="In Transit",
            origin="London, UK",
            destination="Milan, Italy",
            carrier="StockBridge Express",
            type_of_shipment="Air Freight",
            weight="23kg",
            shipment_mode="Air",
            carrier_reference_no="REF123456",
            product="Electronics",
            quantity="2",
            payment_mode="Prepaid",
            total_freight="$150",
            expected_delivery="2025-10-15",
            departure_time="10:00 AM",
            pickup_date="2025-10-10",
            pickup_time="9:00 AM",
            comments="Package cleared customs"
        )
        db.session.add(shipment)
        db.session.commit()

        print("✅ Sample shipment created.")

    # Add test history entry (only if none exist)
    if not ShipmentHistory.query.filter_by(shipment_id=shipment.id).first():
        new_history = ShipmentHistory(
            shipment_id=shipment.id,
            date="2025-10-16",
            time="3:30 PM",
            location="Berlin, Germany",
            status="In Transit",
            updated_by="Admin",
            remarks="Package arrived in Berlin sorting center"
        )
        db.session.add(new_history)
        db.session.commit()
        print("✅ Added test history to shipment.")

if __name__ == "__main__":
    app.run(debug=True)

