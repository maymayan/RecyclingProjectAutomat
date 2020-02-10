import qrcode
import requests
from flask import Flask, render_template

app = Flask(__name__)


r = requests.post("http://localhost:8080/rest/automats/addAutomat",
                  json={"id":"automat1","capacity": 100, "isActive": "true", "numberOfBottles": 0,
                        "location": {"neighborhood": "Cankaya", "street": "Sogutozu", "no": "1"}}  )

@app.route('/')
def welcome_page():
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
    r = requests.get("http://localhost:8080/rest/automats/automat1")

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
                           progress_color=color)


#
# @app.route('/connected/{username}')
# def connection_page():

@app.route('/acceptedBottle')
def acceptBottlePage():
    r = requests.get("http://localhost:8080/rest/automats/automat1")
    numOfBottles = r.json()['numberOfBottles']
    capacity = r.json()['capacity']
    if (capacity == 0 ):
        return "DOLDU"
    numOfBottles = numOfBottles+ 1

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
    return str(numOfBottles)

if __name__ == '__main__':
    app.run()
