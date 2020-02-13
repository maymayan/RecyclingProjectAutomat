from time import sleep

import qrcode
import requests
from flask import Flask, render_template

from picamera import PiCamera

app = Flask(__name__)

r = requests.post("http://localhost:8080/rest/automats/addAutomat",
                  json={"id": "automat1", "capacity": 100, "isActive": "true", "numberOfBottles": 0,
                        "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("./static/qrcode.png")


@app.route('/')
def welcome_page():
    r = requests.get("http://localhost:8080/rest/automats/automat1")
    address = r.json()['location']
    value = 100 - r.json()['capacity']
    color = ""
    if (value == 25):
        color = "success"
    if (value == 50):
        color = "info"
    if (value == 75):
        color = "warning"
    if (value == 100):
        color = "danger"
    return render_template('homepage.html', progress_value=str(int(value)),
                           progress_style="width:" + str(int(value)) + "%",
                           progress_label="%" + str(int(value)) + " dolu",
                           progress_color=color,
                           address_neighborhood=address['neighborhood'], address_street=address['street'],
                           address_no=address[
                               'no'])


@app.route('/connected/<usermail>')
def connection_page(usermail):
    user = requests.get("http://localhost:8080/rest/users/"+usermail)
    name = user.json()['name']
    surname = user.json()['surname']
    balance = user.json()['balance']
    return render_template('afterconnection.html',user_name = name, user_surname = surname, user_balance = balance)


def acceptBottlePage():
    r = requests.get("http://localhost:8080/rest/automats/automat1")
    numOfBottles = r.json()['numberOfBottles']
    capacity = r.json()['capacity']
    if (capacity == 0):
        return "DOLDU"
    numOfBottles = numOfBottles + 1

    if (numOfBottles == 3):
        r1 = requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 75, "isActive": "true",
                                 "numberOfBottles": numOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif (numOfBottles == 6):
        r1 = requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 50, "isActive": "true",
                                 "numberOfBottles": numOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif (numOfBottles == 9):
        r1 = requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 25, "isActive": "true",
                                 "numberOfBottles": numOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif (numOfBottles == 12):
        r1 = requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 0, "isActive": "true",
                                 "numberOfBottles": numOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    else:
        r1 = requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": capacity, "isActive": "true",
                                 "numberOfBottles": numOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    return welcome_page()


@app.route('/verifyBottle')
def verifyBottle():
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture('./static/temp.png')
    camera.stop_preview()
    # model.verify('../static/temp.jpg') here will be adapted after model is created
    camera.close()

    return acceptBottlePage()


if __name__ == '__main__':
    app.run()
