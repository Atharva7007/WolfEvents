from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone

@login.user_loader
def load_user(id):
    return db.session.get(Attendee, int(id))

class Attendee(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=True)

    tickets = db.relationship("Ticket", back_populates="attendee")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Attendee {}>'.format(self.name)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(20), nullable=False)
    ticket_price = db.Column(db.Integer, nullable=False)
    number_seats_left = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())
    
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship("Room", back_populates='events')

    tickets=db.relationship("Ticket", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return '<Event {}>'.format(self.name)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    address = db.Column(db.String(50), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)

    events = db.relationship("Event", back_populates='room', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Room {}>'.format(self.address)
    
    @staticmethod
    def get_room_choices():
        return [(room.id, room.address) for room in Room.query.all()]

# Deal with it later
# class Review(db.Model):
#     pass

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(timezone.utc))
    
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    event = db.relationship("Event", back_populates='tickets')

    attendee_id = db.Column(db.Integer, db.ForeignKey("attendee.id"), nullable=False)
    attendee = db.relationship("Attendee", back_populates="tickets")

    def __repr__(self):
        return '<Ticket {}>'.format(self.address)

