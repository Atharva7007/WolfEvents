from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Length, Regexp
from app.models import Attendee
from app import db
import sqlalchemy as sa

class EventCreationForm(FlaskForm):
    event_name = StringField("Event Name", validators=[DataRequired()])
    category = SelectField("Event Category", choices=[("sports", "Sports"), ("entertainment", "Entertainment"), ("music", "Musical Concert")], validators=[DataRequired()])
    ticket_price = IntegerField("Ticket Price", validators=[DataRequired()])
    date = DateField("Event Date", format='%Y-%m-%d', validators=[DataRequired()])
    room_id = SelectField("Event Room", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Event")

class RoomCreationForm(FlaskForm):
    address = StringField("Location/Address", validators=[DataRequired(), Length(max=200)])
    capacity = IntegerField("Capacity", validators=[DataRequired(), NumberRange(min=1, message="Capacity must be atleast 1.")])
    submit = SubmitField("Create Room")


class LoginForm(FlaskForm):
    email = StringField("Email ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    name = StringField("Your Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
    phone_number = StringField("Phone Number", validators=[
        DataRequired(), 
        Length(min=10, max=10, message="Phone number must be exactly 10 digits"), 
        Regexp(r'^\d{10}$', message="Phone number must be exactly 10 digits")
        ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(Attendee).where(Attendee.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        

class TicketBookingForm(FlaskForm):
    number_of_tickets = IntegerField("Number of Tickets", validators=[DataRequired()])
    submit = SubmitField("Book Ticket")
