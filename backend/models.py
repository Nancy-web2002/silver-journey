# backend/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(20), unique=True, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    receiver_name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="In Transit")

    def to_dict(self):
        return {
            "id": self.id,
            "tracking_code": self.tracking_code,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "origin": self.origin,
            "destination": self.destination,
            "current_location": self.current_location,
            "status": self.status
        }