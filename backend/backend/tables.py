import json
from flask_restful import Resource, abort, fields, inputs, marshal_with, reqparse

from reservations import ReservationModel, db, api, is_free


tables_put_args = reqparse.RequestParser()
tables_put_args.add_argument("status", type=str, help="type \"free\"" ,required=True)
tables_put_args.add_argument("min_seats", type=int, help="How many seats do you need?" ,required=True)
tables_put_args.add_argument("start_date", type=inputs.datetime_from_iso8601, help="input date in format: YYYY-MM-DDTHH:MM" ,required=True)
tables_put_args.add_argument("duration", type=str, help="Give duration in format: HH:MM" ,required=True)


resource_fields = {
    "free_tables": fields.String,
}


class Tables(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = tables_put_args.parse_args()
        if args["status"].upper() != "FREE":
            abort(404, message= "nothing happened, if you want a list of free tables input: \"free\"")

        duration = int(str(args["duration"])[:2])*60 + int(args["duration"][3:]) # translate to minutes
        reservations = ReservationModel.query.all()
        free_seats= []
        taken_seats = []
        for reservation in reservations:
            if not is_free(reservation, args["start_date"], duration):
                if reservation.seat_number not in taken_seats:
                    taken_seats.append(reservation.seat_number)
        with open(f"components/schemas/seats.json", "r") as seats:
          all_seats= json.load(seats)["tables"]
        for seat in all_seats:
            if not seat["number"] in taken_seats:
                if seat["minNumberOfSeats"] <= args["min_seats"] and seat["maxNumberOfSeats"] >= args["min_seats"]:
                    free_seats.append(seat["number"])
        print(free_seats)
        return {"free_tables": free_seats}

