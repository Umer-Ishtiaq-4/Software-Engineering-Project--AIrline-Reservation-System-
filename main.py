
from os import removedirs
import re
from flask import Flask, flash, render_template, request, redirect, session
# from flask_login
# from flask_session import Session
from flask_wtf import FlaskForm

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_login import UserMixin
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from datetime import date, datetime

from numpy import source
from werkzeug.datastructures import UpdateDictMixin


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n \xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data_base.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
admin = Admin(app)


class Data_Base_Flights(db.Model):
    flight_Code = db.Column(db.Integer, primary_key=True)
    flight_source = db.Column(db.String(200), nullable=False)
    flight_destination = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.Date)
    flight_available = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"{self.flight_Code} - {self.flight_source} - {self.flight_destination} - {self.flight_available }"


class Data_Base(db.Model):
    cnic = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(
        db.DateTime, default=datetime.utcnow)
    flight_booked = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f"{self.cnic} - {self.name} - {self.username} - {self.email} - {self.password} - {self.flight_booked}"


@app.route('/')
def Home():
    return render_template('base.html')


@app.route('/payment')
def Payment():
    return render_template('payment.html')


@app.route('/seat-book', methods=['GET', 'POST'])
def Book():
    # print(request.method)
    if session:
        return render_template('seat_book.html')
    else:
        return render_template('login.html')


@ app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        user_found = False
        all = Data_Base.query.all()
        for i in all:
            if (i.email == request.form['email']) and (i.password == request.form['password']):
                user_found = True
                # return render_template('seat_book.html')
                session['username'] = i.username
                # session['cnic'] = i.cnic

                return redirect('/seat-book')
        if not user_found:
            flash('No user found --- Register yourself')
            return(render_template('login.html'))


@app.route('/sign-up', methods=['GET', 'POST'])
def Sign_Up():
    # print(request.method)
    if request.method == "POST":
        unique = True
        allTodo = Data_Base.query.all()
        cn = int(request.form['cnic'])
        for i in allTodo:
            if i.cnic == cn:
                unique = False
                flash('This cnic is already registered')
                return render_template('signup.html')
        if unique:
            # print(request.form['name'])
            if request.method == "POST":
                name = request.form['name']
                cnic = request.form['cnic']
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']
                db_flask = Data_Base(cnic=cnic, name=name, username=username,
                                     email=email, password=password)
                allTodo = Data_Base.query.all()
                db.session.add(db_flask)
                db.session.commit()
                return render_template('login.html')
    else:
        return render_template('signup.html')


@app.route('/logout')
def Logout():
    session.pop('username', None)
    session.pop('email', None)

    print(session)
    return render_template('login.html')


@app.route('/about')
def About():
    return render_template('about.html')


@app.route('/Dec-flight')
def Cancel_Flight():
    # print(session.get('username'))
    username = session.get('username')
    user_data = Data_Base.query.all()
    for i in user_data:
        if i.username == username:
            if i.flight_booked > 1:
                i.flight_booked = i.flight_booked - 1
                db.session.commit()
                flash("The flight has been cancelled!!")
                return render_template('seat_book.html')
            elif i.flight_booked == 0:
                flash("There is no flight booked")
                return render_template('seat_book.html')
            break

    return render_template('seat_book.html')


@app.route('/flight_check', methods=['GET', 'POST'])
def flight():
    source = request.form["custom-select-from"]
    destination = request.form["custom-select-to"]
    flight = Data_Base_Flights.query.all()
    user_data = Data_Base.query.all()
    username = session.get('username')
    # print(user_data)
    flight_found = False
    iter = 0
    for i in flight:
        string = str(i)
        j = 0
        flight_source = False
        flight_dest = False
        for i in string.split(' '):
            # source
            if j == 2:
                if source == i:
                    flight_source = True
                    print(i)
            # destinatiuon
            if j == 4:
                if destination == i:
                    flight_dest = True
                    print(i)
            j += 1
        if flight_source and flight_dest and (flight[iter].flight_available > 0):
            flight_found = True
            flight[iter].flight_available = flight[iter].flight_available - 1
            for i in user_data:
                if i.username == username:
                    i.flight_booked += 1
                    break
            db.session.commit()
            break
        iter += 1
    print(flight)
    if flight_found:
        # flash('Your flight has been booked!!')
        return render_template('payment.html')
    else:
        flash('No flights available for this route!!')
        return render_template('seat_book.html')


def Details():
    data = Data_Base.query.all()
    data_found = False
    for i in data:
        if i:
            data_found = True
        print(i)
        print('\n')
    if not data_found:
        print('No data found!!')


admin.add_view(ModelView(Data_Base, db.session))
admin.add_view(ModelView(Data_Base_Flights, db.session))
if __name__ == '__main__':
    app.debug = False

    app.run()
    # Details()
