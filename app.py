from time import sleep

import pigpio
import pyqrcode
import requests
from flask import Flask, render_template, redirect
from picamera import PiCamera
import cv2

app = Flask(__name__)

r = requests.post("http://192.168.1.6:8080/rest/automats/addAutomat",
                  json={"id": "automat1","overallVolume":10.0, "capacity": 100, "active": "true", "numberOfBottles": 0,
                        "location": {"province": "Ankara", "district": "Cankaya", "neighborhood": "Sogutozu",
                                     "latitude": 39.98, "longitude": 32.75}, "baseConnection": None})

qr= pyqrcode.create("automat1")
qr.svg("./static/qrcode.svg", scale = 8)

scannedBottleBarcode = ""
connectedUser = ""
scannedBottlePoint = 0.0
scannedBottleName = ""
scannedBottleType = ""
pi = pigpio.pi()

@app.route('/')
def welcome_page():
    r = None
    try:
        r = requests.get("http://192.168.1.6:8080/rest/automats/automat1")
    except requests.exceptions.RequestException:
        return render_template('cannotconnectautomat.html')
    requests.post("http://192.168.1.8:8080/connections/directlyCloseConnection/automat1")
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
                           address_province=address['province'], address_district=address['district'],
                           address_neighborhood=address['neighborhood'])


@app.route('/connected/<usermail>')
def connection_page(usermail):
    user = requests.get("http://192.168.1.6:8080/rest/users/" + usermail)
    name = user.json()['name']
    surname = user.json()['surname']
    balance = user.json()['balance']
    global connectedUser
    connectedUser = usermail
    return render_template('afterconnection.html', connected_user=connectedUser, automat_id="automat1", user_name=name,
                           user_surname=surname, user_balance=balance)


@app.route('/scannedBarcode/<barcode>')
def barcodeScanned(barcode):
    bottle = requests.get("http://192.168.1.6:8080/rest/bottles/"+barcode)
    global scannedBottleBarcode
    scannedBottleBarcode = barcode
    global scannedBottlePoint
    scannedBottlePoint = bottle.json()["price"]
    global scannedBottleName
    scannedBottleName = bottle.json()["name"] + " " + bottle.json()["type"]
    global scannedBottleType
    scannedBottleType = bottle.json()["type"]
    openFirst()
    return render_template('afterbarcodescanned.html')


def openFirst():
    sleep(1)
    pi.set_servo_pulsewidth(6, 1500)


@app.route('/opencover')
def openTheCover():
    sleep(1)
    pi.set_servo_pulsewidth(6, 1500)
    return redirect('/scannedBarcode/'+scannedBottleBarcode)


@app.route('/closecover')
def closeTheCover():
    sleep(1)
    pi.set_servo_pulsewidth(6, 500)
    return verifyBottle()


@app.route('/closeCoverOnFail/<barcode>')
def closeCoverOnFail(barcode):
    sleep(1)
    pi.set_servo_pulsewidth(6, 500)
    return redirect('/scannedBarcode/' + barcode, 302)


@app.route('/verifyBottle')
def verifyBottle():
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture('./static/temp.jpg')
    camera.stop_preview()
    global scannedBottleType
    addr = 'http://192.168.1.6:5000'+scannedBottleType
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}
    img = cv2.imread('./static/temp.jpg')
    _, img_encoded = cv2.imencode('.jpg', img)
    response = requests.post(addr, data=img_encoded.tostring(), headers=headers)
    verified = response.json()['message']
    camera.close()
    if (verified):
        return acceptBottlePage()
    else:
        return declineBottlePage()


def acceptBottlePage():
    global scannedBottleBarcode
    global connectedUser
    global scannedBottlePoint
    request_counter = 0
    while (request_counter < 5):
        try:
            update_balance = requests.put(
                "http://192.168.1.6:8080/rest/users/updateBalance/" + connectedUser + "/" + str(scannedBottlePoint))
            change_capacity = requests.put(
                "http://192.168.1.6:8080/rest/automats/changeCapacity/automat1/" + scannedBottleBarcode)
            send_verified = requests.post(
                "http://192.168.1.6:8080/connections/bottleVerification/" + connectedUser + "/automat1/" + scannedBottleBarcode + "/1")
            if change_capacity.json() and update_balance and send_verified:
                return success()
        except requests.exceptions.RequestException:
            if(request_counter<5):
                request_counter += 1
            else:
                return fail()


def success():
    global scannedBottleBarcode
    global connectedUser
    global scannedBottlePoint
    global scannedBottleName
    openBottomLid()
    sleep(1)
    closeBottomLid()
    return render_template('successpage.html', bottle_type=scannedBottleName, point=scannedBottlePoint,
                           connected_user=connectedUser, barcode=scannedBottleBarcode, automat_id="automat1")


def declineBottlePage():
    global scannedBottleBarcode
    global connectedUser
    request_counter = 0
    while (request_counter < 5):
        try:
            sendNotVerified = requests.post(
                "http://192.168.1.6:8080/connections/bottleVerification/" + connectedUser + "/automat1/" + scannedBottleBarcode + "/0")
            if (sendNotVerified.json()):
                return fail()
        except requests.exceptions.RequestException:
            request_counter += 1


def fail():
    global connectedUser
    global scannedBottleBarcode
    openFirst()
    return render_template('failpage.html', connected_user=connectedUser, barcode=scannedBottleBarcode,
                           automat_id="automat1")


def openBottomLid():
    pi.set_servo_pulsewidth(5, 2500)
    sleep(1)

def closeBottomLid():
    pi.set_servo_pulsewidth(5, 500)

if __name__ == '__main__':
    app.run(host = '192.168.1.2')
