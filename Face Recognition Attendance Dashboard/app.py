from flask import (
    Flask,
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from datetime import timedelta, datetime
from flask_mail import Mail, Message
from controller.controller import Ctr
from dao.dao import *

app = Flask(__name__)

app.config["SECRET_KEY"] = "iot19"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "ddki1912@gmail.com"
app.config["MAIL_PASSWORD"] = "xysx z rxn uz jv emg t"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.permanent_session_lifetime = timedelta(minutes=60)
app.register_blueprint(Ctr)

mail = Mail(app)


def send_email(teacher_email):
    today = datetime.today().strftime("%Y-%m-%d")
    students, student_attendance = get_class_attendance(selected_date=today)

    recipients = []
    for key, value in student_attendance.items():
        if value == "":
            recipients.append(students[key]["email"])

    try:
        msg = Message(
            "Attendance Email", sender="ddki1912@gmail.com", recipients=recipients
        )
        msg.body = "You were absent from the class today!"
        mail.send(msg)

    except Exception as e:
        print(f"Error: {e}")


@app.route("/send_attendance_email", methods=["POST"])
def send_attendance_email():
    if not session.get("teacher"):
        return render_template("login.html")

    if request.method == "POST":
        teacher_email = session["teacher"]["email"]

        send_email(teacher_email=teacher_email)

        return "Email sent successfully!"


if __name__ == "__main__":
    app.run(port=8080, debug=True)
