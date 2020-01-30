import qrcode
from flask import Flask, render_template

app = Flask(__name__)


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

    value = "25"
    return render_template('homepage.html', progress_value=value, progress_style="width:"+value+ "%",
                           progress_label="%" + value + " dolu",
                           progress_color="info")


if __name__ == '__main__':
    app.run()
