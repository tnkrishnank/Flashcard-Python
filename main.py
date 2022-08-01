import os
import sys
import time
import shutil
import pathlib
import datetime
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import and_

from flask import *
from flask_mail import *
from random import *

from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine('postgresql://postgres:admin@localhost:5432/Flashcard')

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = '{EMAIL_ID}'  
app.config['MAIL_PASSWORD'] = '{EMAIL_PASSWORD}'
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  

mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/Flashcard"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

global selectedDeck
selectedDeck = 0

global selectedCard
selectedCard = 0

global previousVisit
previousVisit = ""

global qns
qns = []

global pointer
pointer = 0

global title
title = ""

global msgDisp
msgDisp = ""

global name
name = ""

global username
username = ""

global email
email = ""

global password
password = ""

global generatedOTP
generatedOTP = 0

global otpCount
otpCount = 0

global startTime
startTime = 0

class uDetails(db.Model):
    __tablename__ = "uDetails"
    uID = db.Column(db.Integer, primary_key = True)
    fName = db.Column(db.String, nullable = False)
    pwd = db.Column(db.String, nullable = False)
    enKey = db.Column(db.String, nullable = False)
    lastVisited = db.Column(db.String, nullable = False)

    def __init__(self, a, b, c, d, e):
        self.uID = a
        self.fName = b
        self.pwd = c
        self.enKey = d
        self.lastVisited = e

class uName(db.Model):
    __tablename__ = "uName"
    uID = db.Column(db.Integer, db.ForeignKey("uDetails.uID"), primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)

    def __init__(self, a, b):
        self.uID = a
        self.username = b

class uEmail(db.Model):
    __tablename__ = "uEmail"
    uID = db.Column(db.Integer, db.ForeignKey("uDetails.uID"), primary_key = True)
    email = db.Column(db.String, unique = True, nullable = False)

    def __init__(self, a, b):
        self.uID = a
        self.email = b

class uDeck(db.Model):
    __tablename__ = "uDeck"
    uID = db.Column(db.Integer, db.ForeignKey("uDetails.uID"), primary_key = True)
    dID = db.Column(db.Integer, unique = True, primary_key = True)
    dName = db.Column(db.String, nullable = False)

    def __init__(self, a, b, c):
        self.uID = a
        self.dID = b
        self.dName = c

class qDeck(db.Model):
    __tablename__ = "qDeck"
    qID = db.Column(db.Integer, primary_key = True)
    dID = db.Column(db.Integer, db.ForeignKey("uDeck.dID"), nullable = False)

    def __init__(self, a, b):
        self.qID = a
        self.dID = b

class questionAnswer(db.Model):
    __tablename__ = "questionAnswer"
    qID = db.Column(db.Integer, db.ForeignKey("qDeck.qID"), primary_key = True)
    question = db.Column(db.String, nullable = False)
    answer = db.Column(db.String, nullable = False)

    def __init__(self, a, b, c):
        self.qID = a
        self.question = b
        self.answer = c

class qStat(db.Model):
    __tablename__ = "qStat"
    qID = db.Column(db.Integer, db.ForeignKey("qDeck.qID"), primary_key = True)
    easy = db.Column(db.Integer, nullable = False)
    medium = db.Column(db.Integer, nullable = False)
    hard = db.Column(db.Integer, nullable = False)
    attempts = db.Column(db.Integer, nullable = False)

    def __init__(self, a, b = 0, c = 0, d = 0, e = 0):
        self.qID = a
        self.easy = b
        self.medium = c
        self.hard = d
        self.attempts = e

def isValidUsername(s):
    special_characters = "\!@#$%^&*()-+?_=,<>/'"

    if len(s) >= 5:
        for i in s:
            if i in special_characters:
                return False
    else:
        return False

    return True

def isValidPassword(s):
    if len(s) >= 8:
        for i in s:
            if i.isupper():
                return True

    return False

@app.route("/addCard.html", methods = ["GET", "POST"])
def addCard():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            question = request.form["question"]
            answer = request.form["answer"]

            q = db.session.query(func.max(qDeck.qID)).scalar()

            if q == None:
                q = 0
            
            q = int(q) + 1

            sq = "INSERT INTO \"qDeck\" VALUES (" + str(q) + ", " + str(selectedDeck) + ");"
            with engine.connect() as con:
                con.execute(sq)
            db.session.commit()

            sq = "INSERT INTO \"questionAnswer\" VALUES (" + str(q) + ", '" + str(question) + "', '" + str(answer) + "');"
            with engine.connect() as con:
                con.execute(sq)
            db.session.commit()

            title = "CARD ADDED"
            msgDisp = "CARD ADDED SUCCESSFULLY"
            return redirect("/msgDisplay.html")
        else:
            return render_template("addCard.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/addDC.html", methods = ["GET", "POST"])
def addDC():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        return render_template("addDC.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/addDeck.html", methods = ["GET", "POST"])
def addDeck():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            dName = request.form["deckName"]

            q = db.session.query(func.max(uDeck.dID)).scalar()

            if q == None:
                q = 0

            q = int(q) + 1

            sq = "INSERT INTO \"uDeck\" VALUES (" + str(request.cookies.get('cUser')) + ", " + str(q) + ", '" + str(dName) + "');"
            with engine.connect() as con:
                con.execute(sq)
            db.session.commit()

            title = "DECK ADDED"
            msgDisp = "DECK ADDED SUCCESSFULLY"
            return redirect("/msgDisplay.html")
        else:
            return render_template("addDeck.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/analysis.html", methods = ["GET", "POST"])
def analysis():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global qns

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        path = pathlib.Path(__file__).parent.absolute()

        path = str(path) + "\static\images" + "\\analysis\\" + str(request.cookies.get('cUser'))

        pathlib.Path(path).mkdir(parents = True, exist_ok = True)

        q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

        decks = []
        for i in q:
            decks.append(i.dID)

        q = qDeck.query.filter(qDeck.dID.in_(decks)).all()

        qns = []
        for i in q:
            qns.append(i.qID)

        q = qStat.query.filter(qStat.qID.in_(qns)).all()

        values = {}
        values["EASY"] = 0
        values["MEDIUM"] = 0
        values["HARD"] = 0
        values["ATTEMPTED"] = 0

        for i in q:
            values["EASY"] += i.easy
            values["MEDIUM"] += i.medium
            values["HARD"] += i.hard
            values["ATTEMPTED"] += i.attempts

        x = list(values.keys())
        y = list(values.values())

        plt.bar(range(len(values)), y, tick_label = x)
        filename = path + "\graph-01.jpg"

        plt.savefig(filename)

        path = "../static/images/analysis/" + str(request.cookies.get('cUser')) + "/"

        return render_template("analysis.html", imagePath = path, lv = previousVisit)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cardAddSelect.html", methods=["GET", "POST"])
def cardAddSelect():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global selectedDeck

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            selectedDeck = request.form["selectedDeck"]

            return redirect("/addCard.html")
        else:
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "SELECT DECK"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else:
                return render_template("cardAddSelect.html", decks = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cardDelSelect.html", methods=["GET", "POST"])
def cardDelSelect():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global selectedDeck

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            selectedDeck = request.form["selectedDeck"]

            return redirect("/delCard.html")
        else:
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "SELECT DECK"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else:
                return render_template("cardDelSelect.html", decks = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cardEditSelect.html", methods = ["GET", "POST"])
def cardEditSelect():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global selectedDeck

    if 'cUser' not in request.cookies:
        return redirect("/")

    try :
        if request.method == "POST":
            selectedDeck = request.form["selectedDeck"]

            return redirect("/editCard.html")
        else :
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "SELECT DECK"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else :
                return render_template("cardEditSelect.html", decks = q)
    except :
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cEmail.html", methods = ["GET", "POST"])
def cEmail():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global email
    global generatedOTP
    global otpCount
    global startTime

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            if request.form["form-button"] == "password":
                password = request.form["password"]

                q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser')))

                key = bytes(q[0].enKey, "utf-8")
                cipher_suite = Fernet(key)
                checkPassword = bytes(q[0].pwd, "utf-8")
                checkPassword = cipher_suite.decrypt(checkPassword)
                checkPassword = checkPassword.decode("utf-8")

                if checkPassword == password:
                    return render_template("cEmail.html", title = "CHANGE EMAIL", cardTitle = "NEW EMAIL")
                else:
                    return render_template("cEmail.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True, passMsg = "INVALID PASSWORD !")
            elif request.form["form-button"] == "newEmail":
                newEmail = request.form["newEmail"]

                email = newEmail

                q = uEmail.query.all()

                for i in q:
                    if i.email == newEmail:
                        return render_template("cEmail.html", title = "CHANGE EMAIL", cardTitle = "NEW EMAIL", emailMsg = "ACCOUNT ALREADY EXISTS !")

                otpCount = 0

                generatedOTP = randint(100000, 999999)

                path = pathlib.Path(__file__).parent.absolute()
                path = str(path) + "\static\images" + "\\flashcard_mail_logo.png"

                msg = Message('OTP - EMAIL CHANGE', sender = 'mail.flashcard@gmail.com', recipients = [email])

                with app.open_resource(str(path)) as fp :
                    msg.attach("flashcard_mail_logo.png", "image/png", fp.read(), 'inline', headers = [['Content-ID', '<flashcard_mail_logo>']])

                q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

                msg.html = render_template("mailTemplate.html", name = q[0].fName, text = "for email change", otp = generatedOTP)
                mail.send(msg)

                startTime = int(time.time())

                return render_template("cEmail.html", title = "ENTER OTP", cardTitle = "OTP SENT SUCCESSFULLY", getOTP = True)
            else:
                otp = request.form["otp"]

                endTime = int(time.time())

                if (endTime - startTime) > 120:
                    title = "OTP EXPIRED"
                    msgDisp = "OTP EXPIRED"
                    return redirect("/msgDisplay.html")

                if otpCount >= 3:
                    title = "TIMED OUT"
                    msgDisp = "OTP TIMED OUT"
                    return redirect("/msgDisplay.html")

                if otp == str(generatedOTP):
                    q = uEmail.query.filter_by(uID=int(request.cookies.get('cUser')))

                    q[0].email = email
                    db.session.commit()

                    email = ""

                    title = "EMAIL CHANGED"
                    msgDisp = "EMAIL CHANGED SUCCESSFULLY"
                    return redirect("/msgDisplay.html")
                else:
                    otpCount = otpCount + 1

                    if otpCount >= 3:
                        title = "TIMED OUT"
                        msgDisp = "OTP TIMED OUT"
                        return redirect("/msgDisplay.html")

                    return render_template("cEmail.html", title = "ENTER OTP", cardTitle = "OTP SENT SUCCESSFULLY", getOTP = True, otpMsg = "INVALID OTP !")
        else:
            return render_template("cEmail.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cName.html", methods = ["GET", "POST"])
def cName():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            newName = request.form["newName"]

            q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser'))).all()
            q[0].fName = newName
            db.session.commit()

            title = "NAME CHANGED"
            msgDisp = "NAME CHANGED SUCCESSFULLY"
            return redirect("/msgDisplay.html")
        else:
            return render_template("cName.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cPass.html", methods = ["GET", "POST"])
def cPass():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            if request.form["form-button"] == "password":
                password = request.form["password"]

                q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser')))

                key = bytes(q[0].enKey, "utf-8")
                cipher_suite = Fernet(key)
                checkPassword = bytes(q[0].pwd, "utf-8")
                checkPassword = cipher_suite.decrypt(checkPassword)
                checkPassword = checkPassword.decode("utf-8")

                if checkPassword == password:
                    return render_template("cPass.html", title = "CHANGE PASSWORD", cardTitle = "NEW PASSWORD", getPassword = False)
                else:
                    return render_template("cPass.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True, passMsg = "INVALID PASSWORD !")
            else:
                newPassword = request.form["newPassword"]
                reNewPassword = request.form["re-newPassword"]

                q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser')))

                key = bytes(q[0].enKey, "utf-8")
                cipher_suite = Fernet(key)
                checkPassword = bytes(q[0].pwd, "utf-8")
                checkPassword = cipher_suite.decrypt(checkPassword)
                checkPassword = checkPassword.decode("utf-8")

                if newPassword != checkPassword:
                    if isValidPassword(newPassword):
                        if newPassword == reNewPassword:
                            key = Fernet.generate_key()
                            cipher_suite = Fernet(key)
                            password = bytes(newPassword, "utf-8")
                            password = cipher_suite.encrypt(password)
                            password = password.decode("utf-8")

                            q[0].pwd = password
                            db.session.commit()

                            key = key.decode("utf-8")
                            q[0].enKey = key
                            db.session.commit()
                        
                            title = "PASSWORD CHANGED"
                            msgDisp = "PASSWORD CHANGED SUCCESSFULLY"
                            return redirect("/msgDisplay.html")
                        else:
                            return render_template("cPass.html", title = "CHANGE PASSWORD", cardTitle = "NEW PASSWORD", getPassword = False, reNewPassMsg = "PASSWORDS DO NOT MATCH !")
                    else:
                        return render_template("cPass.html", title = "CHANGE PASSWORD", cardTitle = "NEW PASSWORD", getPassword = False, newPassMsg = "Atleast 8 characters. Atleast one character in Uppercase !")
                else:
                    return render_template("cPass.html", title = "CHANGE PASSWORD", cardTitle = "NEW PASSWORD", getPassword = False, newPassMsg = "CURRENT AND NEW PASSWORD ARE SAME !")
        else :
            return render_template("cPass.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/cUname.html", methods = ["GET", "POST"])
def cUname():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            if request.form["form-button"] == "password":
                password = request.form["password"]

                q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser')))

                key = bytes(q[0].enKey, "utf-8")
                cipher_suite = Fernet(key)
                checkPassword = bytes(q[0].pwd, "utf-8")
                checkPassword = cipher_suite.decrypt(checkPassword)
                checkPassword = checkPassword.decode("utf-8")

                if checkPassword == password:
                    return render_template("cUname.html", title = "CHANGE USERNAME", cardTitle = "NEW USERNAME", getPassword = False)
                else:
                    return render_template("cUname.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True, passMsg = "INVALID PASSWORD !")
            else:
                newUsername = request.form["newUsername"]

                if isValidUsername(newUsername):
                    q = uName.query.all()

                    for i in q:
                        if i.username == newUsername:
                            return render_template("cUname.html", title = "CHANGE USERNAME", cardTitle = "NEW USERNAME", getPassword = False, uNameMsg = "USER ALREADY EXISTS !")

                    q = uName.query.filter_by(uID=int(request.cookies.get('cUser')))

                    q[0].username = newUsername
                    db.session.commit()

                    title = "USERNAME CHANGED"
                    msgDisp = "USERNAME CHANGED SUCCESSFULLY"
                    return redirect("/msgDisplay.html")
                else:
                    return render_template("cUname.html", title = "CHANGE USERNAME", cardTitle = "NEW USERNAME", getPassword = False, uNameMsg = "Atleast 5 characters. No special characters allowed !")
        else:
            return render_template("cUname.html", title = "CONFIRM", cardTitle = "ENTER YOUR PASSWORD", getPassword = True)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/dashboard.html", methods = ["GET", "POST"])
def dashboard():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            if request.form["logout"] == "signout":
                resp = make_response(redirect('/'))
                resp.set_cookie('cUser', '', max_age=0)

                return resp
            else:
                pass
        else:
            q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            q = "HELLO ! " + q[0].fName

            return render_template("dashboard.html", welcome = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/delAcc.html", methods = ["GET", "POST"])
def delAcc():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            password = request.form["password"]

            q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser')))

            key = bytes(q[0].enKey, "utf-8")
            cipher_suite = Fernet(key)
            checkPassword = bytes(q[0].pwd, "utf-8")
            checkPassword = cipher_suite.decrypt(checkPassword)
            checkPassword = checkPassword.decode("utf-8")

            if checkPassword == password:
                sq = "DELETE FROM \"uDetails\" WHERE \"uID\" = " + str(request.cookies.get('cUser')) + ";"
                with engine.connect() as con :
                    con.execute(sq)
                db.session.commit()

                current_dir = os.path.abspath(os.path.dirname(__file__))
                current_dir = os.path.join(current_dir, "static")
                current_dir = os.path.join(current_dir, "images")
                current_dir = os.path.join(current_dir, "analysis")
                current_dir = os.path.join(current_dir, str(request.cookies.get('cUser')))

                shutil.rmtree(current_dir, ignore_errors=True)

                resp = make_response(redirect('/'))
                resp.set_cookie('cUser', '', max_age=0)

                return resp
            else :
                return render_template("delAcc.html", passMsg = "INVALID PASSWORD !")
        else:
            return render_template("delAcc.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/delCard.html", methods = ["GET", "POST"])
def delCard():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global qns

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            selectedCard = request.form["selectedCard"]        

            sq = "DELETE FROM \"qDeck\" WHERE \"qID\" = " + str(selectedCard) + ";"
            with engine.connect() as con:
                con.execute(sq)
            db.session.commit()

            title = "CARD DELETED"
            msgDisp = "CARD DELETED SUCCESSFULLY"
            return redirect("/msgDisplay.html")
        else:
            q = qDeck.query.filter_by(dID=selectedDeck).all()

            qns = []
            for i in q:
                qns.append(i.qID)

            q = questionAnswer.query.filter(questionAnswer.qID.in_(qns)).all()

            if len(q) == 0:
                title = "CARD SELECT"
                msgDisp = "NO CARDS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else:
                return render_template("delCard.html", cards = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/delDC.html", methods = ["GET", "POST"])
def delDC():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        return render_template("delDC.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/delDeck.html", methods = ["GET", "POST"])
def delDeck():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            selectedDeck = request.form["selectedDeck"]

            sq = "DELETE FROM \"uDeck\" WHERE \"dID\" = " + str(selectedDeck) + ";"
            with engine.connect() as con:
                con.execute(sq)
            db.session.commit()

            title = "DECK DELETED"
            msgDisp = "DECK DELETED SUCCESSFULLY"
            return redirect("/msgDisplay.html")
        else:
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "DECK SELECT"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else:
                return render_template("delDeck.html", decks = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/editCard.html", methods = ["GET", "POST"])
def editCard():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global qns
    global selectedCard

    if 'cUser' not in request.cookies:
        return redirect("/")

    try :
        if request.method == "POST":
            if request.form["selectedCard"] == "editCard":
                newQuestion = request.form["question"]
                newAnswer = request.form["answer"]

                q = questionAnswer.query.filter_by(qID=selectedCard)

                q[0].question = newQuestion
                q[0].answer = newAnswer
                db.session.commit()

                title = "CARD EDITED"
                msgDisp = "CARD EDITED SUCCESSFULLY"
                return redirect("/msgDisplay.html")
            else:
                selectedCard = request.form["selectedCard"]

                q = questionAnswer.query.filter_by(qID=selectedCard)

                return render_template("editCard.html", defaultQuestion = q[0].question, defaultAnswer = q[0].answer, title = "EDIT CARD")
        else :
            q = qDeck.query.filter_by(dID=selectedDeck).all()

            qns = []
            for i in q:
                qns.append(i.qID)

            q = questionAnswer.query.filter(questionAnswer.qID.in_(qns)).all()

            if len(q) == 0:
                title = "CARD SELECT"
                msgDisp = "NO CARDS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else :
                return render_template("editCard.html", cards = q, title = "SELECT CARD")
    except :
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/editDC.html", methods = ["GET", "POST"])
def editDC():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        return render_template("editDC.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/editDeck.html", methods = ["GET", "POST"])
def editDeck():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global selectedDeck

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if request.method == "POST":
            if request.form["selectedDeck"] == "newDeckName":
                newDeckName = request.form["newDeckName"]

                q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).filter_by(dID=selectedDeck).all()

                q[0].dName = newDeckName
                db.session.commit()

                title = "DECK NAME CHANGED"
                msgDisp = "DECK NAME CHANGED SUCCESSFULLY"
                return redirect("/msgDisplay.html")
            else:
                selectedDeck = request.form["selectedDeck"]

                return render_template("editDeck.html")
        else:
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "DECK SELECT"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else :
                return render_template("editDeck.html", decks = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/forgot.html", methods = ["GET", "POST"])
def forgot():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global email
    global generatedOTP
    global otpCount
    global startTime

    try:
        if request.method == "POST":
            if request.form["submitButton"] == "checkOTP":
                otp = request.form["otp"]

                endTime = int(time.time())

                if (endTime - startTime) > 120:
                    title = "OTP EXPIRED"
                    msgDisp = "OTP EXPIRED"
                    return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                if otpCount >= 3:
                    title = "TIMED OUT"
                    msgDisp = "OTP TIMED OUT"
                    return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                if otp == str(generatedOTP):
                    return render_template("forgot.html", fo = "NEW PASSWORD")
                else:
                    otpCount = otpCount + 1

                    if otpCount >= 3:
                        title = "TIMED OUT"
                        msgDisp = "OTP TIMED OUT"
                        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                    return render_template("forgot.html", enterOTP = True, otpMsg = "INVALID OTP !", fo = "ENTER OTP")
            elif request.form["submitButton"] == "sendOTP":
                email = request.form["email"]

                q = uEmail.query.all()

                t = 0
                for i in q:
                    if i.email == email:
                        t = 1
                        break

                otpCount = 0
                
                generatedOTP = randint(100000, 999999)

                if t == 1:
                    p = uName.query.filter_by(uID=i.uID).all()

                    r = uDetails.query.filter_by(uID=i.uID).all()

                    path = pathlib.Path(__file__).parent.absolute()
                    path = str(path) + "\static\images" + "\\flashcard_mail_logo.png"

                    msg = Message('OTP - RESET ACCOUNT', sender = 'mail.flashcard@gmail.com', recipients = [email])

                    with app.open_resource(str(path)) as fp :
                        msg.attach("flashcard_mail_logo.png", "image/png", fp.read(), 'inline', headers = [['Content-ID', '<flashcard_mail_logo>']])

                    msg.html = render_template("mailTemplate.html", name = r[0].fName, text = "to reset your account", otp = generatedOTP, forgot = True, uName = p[0].username)
                    mail.send(msg)

                    startTime = int(time.time())

                    return render_template("forgot.html", enterOTP = True, fo = "ENTER OTP")
                else:
                    return render_template("forgot.html", enterEmail = True, mailMsg = "ACCOUNT DOES NOT EXIST!", f0 = "ENTER EMAIL")
            else:
                newPassword = request.form["newPassword"]
                reNewPassword = request.form["re-newPassword"]

                if isValidPassword(newPassword):
                    if newPassword == reNewPassword:
                        q = uEmail.query.filter_by(email=email)

                        p = uDetails.query.filter_by(uID=q[0].uID)

                        resp = make_response(redirect('/dashboard.html'))
                        resp.set_cookie('cUser', str(p[0].uID), max_age=604800)

                        key = Fernet.generate_key()
                        cipher_suite = Fernet(key)
                        password = bytes(newPassword, "utf-8")
                        password = cipher_suite.encrypt(password)
                        password = password.decode("utf-8")

                        p[0].pwd = password
                        db.session.commit()

                        key = key.decode("utf-8")
                        p[0].enKey = key
                        db.session.commit()

                        return resp
                    else:
                        return render_template("forgot.html", reNewPasswordMsg = "PASSWORDS DO NOT MATCH !", fo = "NEW PASSWORD")
                else:
                    return render_template("forgot.html", newPasswordMsg = "Atleast 8 characters. Atleast one character in Uppercase !", fo = "NEW PASSWORD")
        else:
            return render_template("forgot.html", enterEmail = True, fo = "ENTER EMAIL")
    except:
        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/", methods = ["GET", "POST"])
def signin():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    try:
        if 'cUser' in request.cookies:
            return redirect('/dashboard.html')

        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            q = uName.query.all()

            t = 0
            for i in q:
                p = uEmail.query.filter_by(uID=i.uID).all()

                if i.username == username or p[0].email == username:
                    t = 1

                    r = uDetails.query.filter_by(uID=i.uID).all()

                    key = bytes(r[0].enKey, "utf-8")
                    cipher_suite = Fernet(key)
                    checkPassword = bytes(r[0].pwd, "utf-8")
                    checkPassword = cipher_suite.decrypt(checkPassword)
                    checkPassword = checkPassword.decode("utf-8")

                    if checkPassword == password:
                        now = datetime.datetime.now()

                        dateTime = now.strftime("%d/%m/%Y %H:%M:%S")

                        previousVisit = r[0].lastVisited

                        r[0].lastVisited = dateTime
                        db.session.commit()

                        resp = make_response(redirect('/dashboard.html'))
                        resp.set_cookie('cUser', str(r[0].uID), max_age=604800)

                        return resp
                    else:
                        return render_template("index.html", passMsg = "INVALID PASSWORD !")
            if t == 0:
                return render_template("index.html", usrMsg = "INVALID USERNAME OR EMAIL !")
        else:
            return render_template("index.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/msgDisplay.html", methods = ["GET", "POST"])
def msgDisplay():
    if 'cUser' not in request.cookies:
        return redirect("/")

    return render_template("msgDisplay.html", title = title, msgDisp = msgDisp)

@app.route("/profile.html", methods = ["GET", "POST"])
def profile():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        q = uDetails.query.filter_by(uID=int(request.cookies.get('cUser'))).all()
        name = q[0].fName

        p = uName.query.filter_by(uID=q[0].uID).all()
        username = p[0].username
        
        r = uEmail.query.filter_by(uID=q[0].uID).all()
        email = r[0].email

        s = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()
        nd = len(s)

        return render_template("profile.html", name = name, uName = username, email = email, nd = nd)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/review.html", methods=["GET", "POST"])
def review():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global pointer

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        if pointer == len(qns):
            title = "FINISH"
            msgDisp = "END OF DECK"
            return redirect("/msgDisplay.html")

        if request.method == "POST":
            if request.form["submit_button"] == "previous":
                pointer = pointer - 1
                
                q = questionAnswer.query.filter_by(qID=qns[pointer]).all()

                if pointer == 0:
                    return render_template("review.html", questionPassed = True, qnRAns = "QUESTION", question = q[0].question, noPrev = True)
                else:
                    return render_template("review.html", questionPassed = True, qnRAns = "QUESTION", question = q[0].question, noPrev = False)
            elif request.form["submit_button"] == "reveal":
                q = questionAnswer.query.filter_by(qID=qns[pointer]).all()

                p = qStat.query.filter_by(qID=qns[pointer]).all()

                p[0].attempts = p[0].attempts + 1
                db.session.commit()

                return render_template("review.html", questionPassed = False, qnRAns = "ANSWER", question = q[0].answer)
            elif request.form["submit_button"] == "next":
                pointer = pointer + 1

                if pointer == len(qns):
                    title = "FINISH"
                    msgDisp = "END OF DECK"
                    return redirect("/msgDisplay.html")                
                else:
                    q = questionAnswer.query.filter_by(qID=qns[pointer]).all()

                    return render_template("review.html", questionPassed = True, qnRAns = "QUESTION", question = q[0].question, noPrev = False)
            elif request.form["submit_button"] == "easy":
                p = qStat.query.filter_by(qID=qns[pointer]).all()

                p[0].easy = int(p[0].easy) + 1

                db.session.commit()
                pointer = pointer + 1

                return redirect("/review.html")
            elif request.form["submit_button"] == "medium":
                p = qStat.query.filter_by(qID=qns[pointer]).all()

                p[0].medium = p[0].medium + 1

                db.session.commit()
                pointer = pointer + 1

                return redirect("/review.html")
            elif request.form["submit_button"] == "hard":
                p = qStat.query.filter_by(qID=qns[pointer]).all()

                p[0].hard = p[0].hard + 1

                db.session.commit()
                pointer = pointer + 1

                return redirect("/review.html")
        else:
            q = questionAnswer.query.filter_by(qID=qns[pointer]).all()

            if pointer == 0:
                return render_template("review.html", questionPassed = True, qnRAns = "QUESTION", question = q[0].question, noPrev = True)
            else:
                return render_template("review.html", questionPassed = True, qnRAns = "QUESTION", question = q[0].question, noPrev = False)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/settings.html", methods = ["GET", "POST"])
def settings():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        return render_template("settings.html")
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/signup.html", methods = ["GET", "POST"])
def signup():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global name
    global username
    global email
    global password
    global generatedOTP
    global otpCount
    global startTime

    try:
        if request.method == "POST":
            if request.form["submitButton"] == "checkOTP":
                name = request.form["name"]
                username = request.form["username"]
                email = request.form["email"]
                password = request.form["password"]
                reTypePassword = request.form["re-password"]

                if isValidUsername(username):
                    if isValidPassword(password):
                        if password == reTypePassword:
                            q = uName.query.all()

                            for i in q:
                                if i.username == username:
                                    return render_template("signup.html", rePsswdMsg = "USER ALREADY EXISTS !", signupPage = True, signOTP = "SIGN UP")

                            q = uEmail.query.all()

                            for i in q:
                                if i.email == email:
                                    return render_template("signup.html", mailMsg = "EMAIL ALREADY EXISTS !", signupPage = True, signOTP = "SIGN UP")

                            otpCount = 0

                            generatedOTP = randint(100000, 999999)

                            path = pathlib.Path(__file__).parent.absolute()
                            path = str(path) + "\static\images" + "\\flashcard_mail_logo.png"

                            msg = Message('OTP - ACCOUNT VERIFICATION', sender = 'mail.flashcard@gmail.com', recipients = [email])

                            with app.open_resource(str(path)) as fp :
                                msg.attach("flashcard_mail_logo.png", "image/png", fp.read(), 'inline', headers = [['Content-ID', '<flashcard_mail_logo>']])

                            msg.html = render_template("mailTemplate.html", name = name, text = "to verify your account", otp = generatedOTP)
                            mail.send(msg)

                            startTime = int(time.time())

                            return render_template("signup.html", signupPage = False, signOTP = "ENTER OTP")
                        else:
                            return render_template("signup.html", rePsswdMsg = "PASSWORDS DO NOT MATCH !", signupPage = True, signOTP = "SIGN UP")
                    else:
                        return render_template("signup.html", psswdMsg = "Atleast 8 characters. Atleast one character in Uppercase !", signupPage = True, signOTP = "SIGN UP")
                else:
                    return render_template("signup.html", usrMsg = "Atleast 5 characters. No special characters allowed !", signupPage = True, signOTP = "SIGN UP")
            else:
                otp = request.form["otp"]

                endTime = int(time.time())

                if (endTime - startTime) > 120:
                    title = "OTP EXPIRED"
                    msgDisp = "OTP EXPIRED"
                    return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                if otpCount >= 3:
                    title = "TIMED OUT"
                    msgDisp = "OTP TIMED OUT"
                    return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                if otp == str(generatedOTP):
                    key = Fernet.generate_key()
                    cipher_suite = Fernet(key)
                    password = bytes(password, "utf-8")
                    password = cipher_suite.encrypt(password)
                    password = password.decode("utf-8")

                    now = datetime.datetime.now()

                    dateTime = now.strftime("%d/%m/%Y %H:%M:%S")

                    q = db.session.query(func.max(uDetails.uID)).scalar()

                    if q == None:
                        q = 0

                    q = int(q) + 1

                    key = key.decode("utf-8")

                    sq = "INSERT INTO \"uDetails\" VALUES (" + str(int(q)) + ", '" + str(name) + "', '" + str(password) + "', '" + str(key) + "', '" + str(dateTime) + "');"
                    with engine.connect() as con:
                        con.execute(sq)
                    db.session.commit()

                    sq = "INSERT INTO \"uName\" VALUES (" + str(int(q)) + ", '" + str(username) + "');"
                    with engine.connect() as con:
                        con.execute(sq)
                    db.session.commit()

                    sq = "INSERT INTO \"uEmail\" VALUES (" + str(int(q)) + ", '" + str(email) + "');"
                    with engine.connect() as con:
                        con.execute(sq)
                    db.session.commit()

                    name = ""
                    username = ""
                    email = ""
                    password = ""
                    generatedOTP = 0

                    resp = make_response(redirect('/dashboard.html'))
                    resp.set_cookie('cUser', str(q), max_age=604800)

                    return resp
                else:
                    otpCount = otpCount + 1

                    if otpCount >= 3:
                        title = "TIMED OUT"
                        msgDisp = "OTP TIMED OUT"
                        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

                    return render_template("signup.html", otpMsg = "INVALID OTP !", signupPage = False, signOTP = "ENTER OTP")
        else:
            return render_template("signup.html", signupPage = True, signOTP = "SIGN UP")
    except:
        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

@app.route("/study.html", methods=["GET", "POST"])
def study():
    global title
    title = ""

    global msgDisp
    msgDisp = ""

    global qns
    global pointer
    global selectedDeck

    if 'cUser' not in request.cookies:
        return redirect("/")

    try:
        qns = []
        pointer = 0

        if request.method == "POST":
            selectedDeck = request.form["selectedDeck"]

            q = qDeck.query.filter_by(dID=selectedDeck).all()

            for i in q:
                qns.append(i.qID)

            q = questionAnswer.query.filter(questionAnswer.qID.in_(qns)).all()

            return redirect("/review.html")
        else:
            q = uDeck.query.filter_by(uID=int(request.cookies.get('cUser'))).all()

            if len(q) == 0:
                title = "DECK SELECT"
                msgDisp = "NO DECKS AVAILABLE !"
                return redirect("/msgDisplay.html")
            else:
                return render_template("study.html", decks = q)
    except:
        if 'cUser' not in request.cookies:
            return redirect("/")

        title = "404 ERROR"
        msgDisp = "404 ERROR. PAGE NOT FOUND !!!"
        return render_template("msgDisplay.html", title = title, msgDisp = msgDisp, login = True)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        debug = True,
        port = 8080
    )
