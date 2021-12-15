from datetime import datetime, timedelta
from flask_restful import Resource, reqparse, fields, marshal_with, abort, inputs
import uuid
import json
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from send_mails import Mail

app = Flask(__name__)
api= Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///components/schemas/Reservation.db'
db = SQLAlchemy(app)



class ReservationModel(db.Model):
    id = db.Column(db.String, primary_key = True)
    date = db.Column(db.String, nullable = False)
    duration = db.Column(db.Integer, nullable = False)
    seat_number = db.Column(db.Integer, nullable = False)
    fullName = db.Column(db.String, nullable = False)
    phone = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String, nullable = False)
    numberOfSeats = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return (f"Reservation(id ={self.id}, date={self.date}, duration={self.duration}, seat_number={self.seat_number}, fullName={self.fullName}, phone={self.phone}, email={self.email}, numberOfSeats={self.numberOfSeats}")

# db.create_all() <- needed to create new db

reservation_put_args = reqparse.RequestParser()
reservation_put_args.add_argument("date", type=inputs.datetime_from_iso8601, help="give date in format: YYYY-MM-DDTHH:MM" ,required=True)
reservation_put_args.add_argument("duration", type=int, help="set duration time in miuntes", required=True)
reservation_put_args.add_argument("seat_number", type=int, help="number of seats is required" ,required=True)
reservation_put_args.add_argument("fullName", type=str, help="Full name id is required" ,required=True)
reservation_put_args.add_argument("phone", type=int, help="phone number is required" ,required=True)
reservation_put_args.add_argument("email", type=str, help="email is required" ,required=True)
reservation_put_args.add_argument("numberOfSeats", type=int, help="Number of seats is required" ,required=True)

day = reqparse.RequestParser()
day.add_argument("date", type=inputs.datetime_from_iso8601, help="give date in format: YYYY-MM-DDT00" ,required=True)

status = reqparse.RequestParser()
status.add_argument("status", type=str, help="if you want to request cancellation reservation write: \"requested cancellation\"", required=True)

cancellation_id = reqparse.RequestParser()
cancellation_id.add_argument("cancellation_id", type=str, help="if you want to cancel the reservation write cancellation_id which we have sent you on your mailbox", required=True)

resource_fields = {
    "id": fields.String,
    "date": fields.String,
    "duration":fields.Integer,
    "seat_number":fields.Integer,
    "fullName": fields.String,
    "phone":fields.Integer,
    "email": fields.String,
    "numberOfSeats": fields.Integer,
}

def is_free(reservation, start_date, duration):
    end_date =start_date + timedelta(minutes= duration)
    booked_date =  datetime.strptime(reservation.date[2:-3], f'%y-%m-%d %H:%M')
    if booked_date + timedelta(minutes =reservation.duration) < start_date or booked_date > end_date:
        return True
    return False

class Reservation(Resource):
    @marshal_with(resource_fields)
    def post(self):
        args = reservation_put_args.parse_args()
        reservation = ReservationModel(id="", date=args["date"], duration=args["duration"],seat_number=args["seat_number"], fullName=args["fullName"], phone=args["phone"], email=args["email"], numberOfSeats=args["numberOfSeats"] )      
        
        # check if the table exist, is accurate and is free
        with open(f"components/schemas/seats.json", "r") as seats:
            all_seats= json.load(seats)

        if reservation.seat_number >= len(all_seats["tables"]):
            abort(404, message="table number is incorrect")

        wanted_seat = all_seats["tables"][reservation.seat_number]
        if (wanted_seat["minNumberOfSeats"] <= reservation.seat_number and
            wanted_seat["maxNumberOfSeats"] >= reservation.seat_number):
            abort(400, message= "this table does not meet Your requirements")
            
        taken_seats = ReservationModel.query.filter_by(seat_number= reservation.seat_number).all()
        for seat in taken_seats:
            if not is_free(seat, args["date"], args["duration"]):
                abort(400, message ="this seat is already taken")
        
        ID = str(uuid.uuid4())[0:6]
        while ReservationModel.query.filter_by(id = ID).first():
            ID = str(uuid.uuid4())[0:6]
        reservation.id=ID
        db.session.add(reservation)
        db.session.commit()
        Mail(reservation.email, "reservation", reservation.__dict__)
        return reservation, 201

class ListOfReservations(Resource):
    @marshal_with(resource_fields)
    def get(self):
        arg = day.parse_args()
        result = ReservationModel.query.filter(ReservationModel.date.contains(str(arg["date"])[:-8])).all()
        if not result:
            abort(404, message= "Zero reservations in this day")
        return result, 200
        
class Cancelation(Resource):
    def inTime(self, timeOfReservation):
        return datetime.strptime(timeOfReservation, f'%y-%m-%d %H:%M') - datetime.now() > timedelta(hours =2)

    @marshal_with(resource_fields)
    def put(self, ID):
        arg = status.parse_args()
        if (arg["status"]).upper() != "REQUESTED CANCELLATION":
            abort(400, message= "nothing happened, if you want to request cancellation write: \"requested cancellation\"")
        result = ReservationModel.query.filter_by(id = ID).first()
        if not result:
            abort(404, message= "given id of reservation is incorrect") 
        if not self.inTime(result.date[2:-3]):
            abort(405, message= "You cannot cancel the reservation less than 2 hours earlier")
        
        # create cancellation id and save it in json
        with open(f"components/schemas/cancellations.json", "r") as cancellation_array:
            all_ids= json.load(cancellation_array)
        new_id = str(uuid.uuid4())[0:6]
        while new_id in all_ids:
            new_id = str(uuid.uuid4())[0:6]
        all_ids.update({new_id:ID})
        with open(f"components/schemas/cancellations.json", "w") as cancellation_array:
            json.dump(all_ids, cancellation_array, indent=2)

        Mail(result.email, "requested cancellation", {"reservation_id":ID,"verification_code":new_id})
        return result, 200 


    def delete(self, ID):
        arg = cancellation_id.parse_args()
        verification_code = arg["cancellation_id"]
        result = ReservationModel.query.filter_by(id = ID).first()
        if not result:
            abort(404, message= "given id is incorrect") 
        if not self.inTime(result.date[2:-3]):
            abort(405, message= "You cannot cancel the reservation less than 2 hours earlier")

        # verification of cancellation_id
        with open(f"components/schemas/cancellations.json", "r") as cancellation_array:
            all_ids= json.load(cancellation_array)
        if (verification_code not in all_ids) or all_ids[verification_code] != ID:
            abort(404, message= "given cancellation_id is incorrect or do not match your reservation")
        # all cancellation_ids of this client have to be removed
        trash = []
        for id in all_ids:
            if all_ids[id] == ID:
                trash.append(id)
        for id in trash:
            del all_ids[id]
        with open(f"components/schemas/cancellations.json", "w") as cancellation_array:
            json.dump(all_ids, cancellation_array, indent=2)

        Mail(result.email, "cancellation confirmation", {"reservation_id":ID, "message":"Your reservation does not exist from now"})
        db.session.delete(result)
        db.session.commit()
        return ("success", 200)

