from flask import url_for, redirect, render_template, flash, request
from app import app, db
from app.forms import EventCreationForm, RoomCreationForm, LoginForm, RegistrationForm, TicketBookingForm
from app.models import Room, Event, Attendee, Ticket
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="WolfEvents")


@app.route("/create_event", methods=["GET", "POST"])
@login_required
def create_event():
    # Only admin should be able to create a new event
    if not current_user.is_admin:
        flash("You are not authorized to access this page")
        return redirect(url_for("index"))
    
    form = EventCreationForm()
    form.room_id.choices = Room.get_room_choices()

    if form.validate_on_submit():
        room = Room.query.get(form.room_id.data)
        event = Event(
            name = form.event_name.data,
            category = form.category.data,
            ticket_price = form.ticket_price.data,
            date = form.date.data,
            room_id = form.room_id.data,
            number_seats_left = room.capacity
        )
        db.session.add(event)
        db.session.commit()
        flash("Successfully created a new event!")
        return redirect(url_for("index"))
    return render_template("create_event.html", title="New Event", form=form)

@app.route("/list_events")
@login_required
def list_events():
    events = Event.query.all()
    return render_template("list_events.html", title="Events", events=events)

@app.route("/create_room", methods=["GET", "POST"])
@login_required
def create_room():
    # Only admin should be able to create a new room
    if not current_user.is_admin:
        flash("You are not authorized to access this page")
        return redirect(url_for("index"))
    form = RoomCreationForm()

    if form.validate_on_submit():
        room = Room(address=form.address.data, capacity=form.capacity.data)
        db.session.add(room)
        db.session.commit()
        flash("Successfully created a new room!")
        return redirect(url_for('index'))

    return render_template("create_room.html", title="New Room", form=form)

@app.route("/list_rooms")
@login_required
def list_rooms():
    # Onlyy admin should be able to view all rooms
    if not current_user.is_admin:
        flash("You are not authorized to access this page")
        return redirect(url_for("index"))
    rooms = Room.query.all()
    return render_template("list_rooms.html", rooms=rooms)

@app.route('/delete_room/<room_id>', methods=['POST'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    try:
        db.session.delete(room)
        db.session.commit()
        flash('Room deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting room: ' + str(e), 'error')
    return redirect(url_for('list_rooms'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(Attendee).where(Attendee.email == form.email.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password!")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template("login.html", title="Log In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        attendee = Attendee(name=form.name.data, email=form.email.data, phone_number=form.phone_number.data)
        attendee.set_password(form.password.data)
        db.session.add(attendee)
        db.session.commit()
        flash("Congrats! You are now a registered user!")
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/list_attendees")
@login_required
def list_attendees():
    if not current_user.is_admin:
        flash("You are not authorized to access this page")
        return redirect(url_for('index'))
    attendees = Attendee.query.all()
    return render_template("list_attendees.html", attendees=attendees)

@app.route("/book_ticket/<event_id>", methods=["GET", "POST"])
@login_required
def book_ticket(event_id):
    event = Event.query.get(event_id)
    form = TicketBookingForm()

    if form.validate_on_submit():
        number_of_tickets = form.number_of_tickets.data

        if event.number_seats_left >= number_of_tickets:
            event.number_seats_left -= number_of_tickets
            ticket = Ticket(number_of_tickets=number_of_tickets, event_id=event.id, attendee_id=current_user.id)
            db.session.add(ticket)
            db.session.commit()
            flash("Tickets Booked successfully!", "success")
            return redirect(url_for("list_events"))
        else:
            flash('Not enough seats available.', 'danger')

    return render_template("book_ticket.html", form=form, event=event)