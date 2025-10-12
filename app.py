from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random, string

app = Flask(__name__)

CORS (app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shipments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(50), unique=True)
    shipper_name = db.Column(db.String(100))
    shipper_address = db.Column(db.String(200))
    receiver_name = db.Column(db.String(100))
    receiver_address = db.Column(db.String(200))
    receiver_phone = db.Column(db.String(50))
    receiver_email = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    status = db.Column(db.String(50))
    carrier = db.Column(db.String(50))
    type_of_shipment = db.Column(db.String(100))
    weight = db.Column(db.String(50))
    shipment_mode = db.Column(db.String(50))
    carrier_ref_no = db.Column(db.String(50))
    product = db.Column(db.String(100))
    qty = db.Column(db.Integer)
    payment_mode = db.Column(db.String(50))
    total_freight = db.Column(db.String(50))
    expected_delivery = db.Column(db.String(50))
    departure_time = db.Column(db.String(50))
    pickup_date = db.Column(db.String(50))
    pickup_time = db.Column(db.String(50))
    comments = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_tracking_code():
    return "AWB" + ''.join(random.choices(string.digits, k=12))

@app.route('/')
def home():
    return render_template('create_shipment.html')

@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    data = request.form
    tracking_code = generate_tracking_code()

    shipment = Shipment(
        tracking_code=tracking_code,
        shipper_name=data['shipper_name'],
        shipper_address=data['shipper_address'],
        receiver_name=data['receiver_name'],
        receiver_address=data['receiver_address'],
        receiver_phone=data['receiver_phone'],
        receiver_email=data['receiver_email'],
        origin=data['origin'],
        destination=data['destination'],
        status=data['status'],
        carrier=data['carrier'],
        type_of_shipment=data['type_of_shipment'],
        weight=data['weight'],
        shipment_mode=data['shipment_mode'],
        carrier_ref_no=data['carrier_ref_no'],
        product=data['product'],
        qty=data['qty'],
        payment_mode=data['payment_mode'],
        total_freight=data['total_freight'],
        expected_delivery=data['expected_delivery'],
        departure_time=data['departure_time'],
        pickup_date=data['pickup_date'],
        pickup_time=data['pickup_time'],
        comments=data['comments']
    )

    db.session.add(shipment)
    db.session.commit()

    return redirect(url_for('view_shipment', tracking_code=shipment.tracking_code))

@app.route('/shipment/<tracking_code>')
def view_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first_or_404()
    return render_template('print_shipment.html', shipment=shipment, editable=False)

@app.route('/update_shipment/<tracking_code>', methods=['GET', 'POST'])
def update_shipment(tracking_code):
    shipment = Shipment.query.filter_by(tracking_code=tracking_code).first_or_404()

    if request.method == 'POST':
        # Update shipment details
        shipment.status = request.form['status']
        shipment.origin = request.form['origin']
        shipment.destination = request.form['destination']
        shipment.comments = request.form['comments']
        shipment.expected_delivery = request.form['expected_delivery']
        db.session.commit()
        return redirect(url_for('view_shipment', tracking_code=tracking_code))

    return render_template('print_shipment.html', shipment=shipment, editable=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)