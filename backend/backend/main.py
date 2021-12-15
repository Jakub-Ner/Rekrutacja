# before start make sure you run smtpd (send_mails.py)
from tables import Tables
from reservations import app, api, Reservation, ListOfReservations, Cancelation


api.add_resource(Reservation, "/reservations")
api.add_resource(ListOfReservations, "/reservations")
api.add_resource(Cancelation, "/reservations/<string:ID>")
api.add_resource(Tables, "/tables")

if __name__ == "__main__":
    app.run(debug=True)
