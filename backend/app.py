# backend/app.py
#pyright:reportGeneralTypeIssues=false
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Shipment
import random
import string

app = Flask(__name__)

# ---------- Database Configuration ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ---------- Helper Function ----------
def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# ---------- Routes ----------
@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Invalid or missing JSON data"}), 400
    tracking_code = generate_tracking_code()

    shipment = Shipment (
        tracking_code=data['tracking_code'],
        sender_name=data['sender_name'],
        receiver_name=data['receiver_name'],
        origin=data['origin'],
        destination=data['destination'],
        current_location=data['origin'],
        status=data['In Transit']
    )

    db.session.add(shipment)
    db.session.commit()
    return jsonify({"message": "Shipment created successfully!", "tracking_code": "tracking_code"})

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

# ---------- Initialize Database ----------
with app.app_context():
    db.create_all()

if __name__== '__main__':
    app.run(debug=True)