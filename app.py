from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, string

# Initialize app
app = Flask(__name__)
CORS(app)

# ---------- DATABASE CONFIG ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODEL ----------
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(20), unique=True, nullable=False)
    sender_name = db.Column(db.String(100))
    receiver_name = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    current_location = db.Column(db.String(100))
    status = db.Column(db.String(100))

    def to_dict(self):
        return {
            "tracking_code": self.tracking_code,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "origin": self.origin,
            "destination": self.destination,
            "current_location": self.current_location,
            "status": self.status
        }

# ---------- HELPER ----------
def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# ---------- ROUTES ----------
@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.get_json()
    tracking_code = generate_tracking_code()

    shipment = Shipment(
        tracking_code=tracking_code,
        sender_name=data['sender_name'],
        receiver_name=data['receiver_name'],
        origin=data['origin'],
        destination=data['destination'],
        current_location=data['origin'],
        status='In Transit'
    )

    db.session.add(shipment)
    db.session.commit()

    return jsonify({"message": "Shipment created successfully!", "tracking_code": tracking_code})

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    shipment = Shipment.query.filter_by(tracking_code=data['tracking_code']).first()

    if not shipment:
        return jsonify({"error": "Tracking code not found"}), 404

    shipment.current_location = data['current_location']
    shipment.status = data['status']
    db.session.commit()

    return jsonify({"message": "Shipment location updated successfully!"})

@app.route('/track/<tracking_code>', methods=['GET'])
def track_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first()
    if not shipment:
        return jsonify({"error": "Tracking code not found"}), 404
    return jsonify(shipment.to_dict())

# ---------- INIT DB ----------
with app.app_context():
    db.create_all()

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)