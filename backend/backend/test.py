import requests

BASE = "http://127.0.0.1:5000/"


response = requests.post(BASE+"reservations",{"date":"2023-10-27T20:37", "duration":20, "seat_number":20, "fullName":"JAN", "phone":50523432, "email":"kubaner1@gmail.com", "numberOfSeats":3})
print(response.json())

response = requests.get(BASE+"reservations",{ "date":"2023-10-27T10"})
print(response.json())

response = requests.delete(BASE + "reservations/98d80b", params={"cancellation_id":"e809fa"})
print(response.json())
# 
# 
response = requests.get(BASE + "tables", params={"status":"free", "min_seats":3, "start_date":"2023-10-27T20:37", "duration":"02:10"})
print(response.json())
