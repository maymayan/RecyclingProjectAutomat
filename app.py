from time import sleep

import RPi.GPIO as GPIO
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
GPIO.cleanup()
img = qr.make_image(fill_color="black", back_color="white")
img.save("./static/qrcode.png")

scannedBottleBarcode = ""
connectedUser = ""
scannedBottlePoint = 0.0
scannedBottleName = ""


@app.route('/')
def welcome_page():
    r = requests.get("http://localhost:8080/rest/automats/automat1")
    address = r.json()['location']
    value = 100 - int(r.json()['capacity'])
    color = ""
    if (value <= 25 and value >= 0):
        color = "success"
    elif (value <= 50 and value > 25):
        color = "info"
    elif (value <= 75 and value > 50):
        color = "warning"
    elif (value < 100 and value > 75):
        color = "danger"
    elif (value == 100):
        return render_template('outofcapacity.html')

    return render_template('homepage.html', automat_id="automat1", progress_value=str(int(value)),
                           progress_style="width:" + str(int(value)) + "%",
                           progress_label="%" + str(int(value)) + " dolu",
                           progress_color=color,
                           address_neighborhood=address['neighborhood'], address_street=address['street'],
                           address_no=address[
                               'no'])


@app.route('/connected/<usermail>')
def connection_page(usermail):
    user = requests.get("http://localhost:8080/rest/users/" + usermail)
    name = user.json()['name']
    surname = user.json()['surname']
    balance = user.json()['balance']
    global connectedUser
    connectedUser = usermail
    return render_template('afterconnection.html', connected_user=connectedUser, automat_id="automat1", user_name=name,
                           user_surname=surname, user_balance=balance)


@app.route('/scannedBarcode/<barcode>')
def barcodeScanned(barcode):
    bottle = requests.get("http://localhost:8080/rest/bottles/"+barcode)
    global scannedBottleBarcode
    scannedBottleBarcode = barcode
    global scannedBottlePoint
    scannedBottlePoint = bottle.json()["price"]
    global scannedBottleName
    scannedBottleName = bottle.json()["name"] + " " + bottle.json()["type"]
    openFirst()
    return render_template('afterbarcodescanned.html')


def openFirst():
    servoPIN = 6
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2.5)
    p.ChangeDutyCycle(12.5)
    sleep(0.5)
    GPIO.cleanup()
    sleep(0.5)


@app.route('/opencover')
def openTheCover():
    servoPIN = 6
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2.5)
    p.ChangeDutyCycle(12.5)
    sleep(0.5)
    GPIO.cleanup()
    sleep(0.5)


@app.route('/closecover')
def closeTheCover():
    servoPIN = 6
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(12.5)
    p.ChangeDutyCycle(2.5)
    sleep(0.5)
    GPIO.cleanup()
    sleep(0.5)
    return verifyBottle()


@app.route('/verifyBottle')
def verifyBottle():
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture('./static/temp.png')
    camera.stop_preview()
    verified = True  # model.verify('../static/temp.jpg') here will be adapted after model is created
    camera.close()
    if (verified):
        return acceptBottlePage()
    else:
        return "Kabul edilmedi"


def acceptBottlePage():
    automat = requests.get("http://localhost:8080/rest/automats/automat1")
    numberOfBottles = automat.json()['numberOfBottles']
    capacity = automat.json()['capacity']
    if (capacity == 0):
        return "DOLDU"
    numberOfBottles = numberOfBottles + 1

    if numberOfBottles == 3:
        requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 75, "isActive": "true",
                                 "numberOfBottles": numberOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif numberOfBottles == 6:
        requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 50, "isActive": "true",
                                 "numberOfBottles": numberOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif numberOfBottles == 9:
        requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 25, "isActive": "true",
                                 "numberOfBottles": numberOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    elif numberOfBottles == 12:
        requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": 0, "isActive": "true",
                                 "numberOfBottles": numberOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    else:
        requests.post("http://localhost:8080/rest/automats/addAutomat",
                           json={"id": "automat1", "capacity": capacity, "isActive": "true",
                                 "numberOfBottles": numberOfBottles,
                                 "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}})
    return success()


def success():
    openBottomLid()
    sleep(1)
    closeBottomLid()
    global scannedBottlePoint
    global connectedUser
    link = "http://localhost:8080/rest/users/updateBalance/" + connectedUser + "/" + str(scannedBottlePoint)
    requests.put(link)
    global scannedBottleBarcode
    return render_template('successpage.html', bottle_type=scannedBottleName, point=scannedBottlePoint,
                           connected_user=connectedUser)


def openBottomLid():
    sleep(1)
    servoPIN = 5
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2.5)
    p.ChangeDutyCycle(7.5)
    sleep(1)
    GPIO.cleanup()

def closeBottomLid():
    sleep(1)
    servoPIN = 5
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(7.5)
    p.ChangeDutyCycle(2.5)
    sleep(1)
    GPIO.cleanup()

if __name__ == '__main__':
    app.run()
