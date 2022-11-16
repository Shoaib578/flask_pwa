# Todo: HASH PASSWORD
# Todo: PASSWORD THE DATABASE
import os
import mimetypes
import os.path
import re
from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE
import uuid
import random
import math
from geopy.geocoders import Nominatim
from flask import Flask, current_app, render_template, request, redirect, url_for, session, make_response, send_from_directory
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
# from flask_ngrok import run_with_ngrok
import ntplib
from time import ctime
import pandas as pd
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow



# For PWA deployment ngrok is to be removed.

# template_dir = os.path.abspath('D:/InternWork/PythonDocker - Flask/template')
app = Flask(__name__, template_folder='templates')
# run_with_ngrok(app)

#after deployment database uri and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


#running locally database uri and secret key
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/timeclock'
# app.config['SECRET_KEY'] = "ajsdojaosdjo"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'timeclockaktus@gmail.com'
app.config['MAIL_PASSWORD'] = 'ziejscjumlsducgf'
# email password: adminPassword123
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
ma= Marshmallow(app)
db = SQLAlchemy(app)
mail = Mail(app)
geocoder = Nominatim(user_agent='TimeClock')




class userview(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100),nullable=True)
    direction = db.Column(db.String(100),nullable=True)
    location = db.Column(db.String(100),nullable=True)
    time = db.Column(db.String(100),nullable=True)
    servertime = db.Column(db.String(100),nullable=True)

class UserViewSchema(ma.Schema):
    class Meta:
        fields = ("id","username","direction","location","time","servertime")




class users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100),nullable=True)
    email = db.Column(db.String(100),nullable=True)
    password = db.Column(db.String(255),nullable=True)
    macaddress = db.Column(db.String(100),nullable=True)
    admin = db.Column(db.Integer(),nullable=True)
    superadmin = db.Column(db.Integer(),nullable=True)
    recovery = db.Column(db.String(100),nullable=True)

class UsersSchema(ma.Schema):
    class Meta:
        fields = ("id","username","email","password","macaddress","admin","superadmin","recovery")

class clock(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100),nullable=True)
    direction = db.Column(db.String(100),nullable=True)
    location = db.Column(db.String(100),nullable=True)
    time = db.Column(db.String(100),nullable=True)
    servertime = db.Column(db.String(100),nullable=True)


class ClockSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "direction", "location", "time", "servertime")


# Run in MySQL Workbench
# USE `TimeClock`;
# CREATE TABLE IF NOT EXISTS `users` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `username` varchar(100) NOT NULL,
# `email` varchar(100) NOT NULL,
# `password` varchar(255) NOT NULL,
# `macaddress` varchar(255) NOT NULL,
# `admin` int(1) NOT NULL,
# `superadmin` int(1) NOT NULL,
# `recovery` varchar(6) NULL,
# PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
# INSERT INTO `users` (`id`, `username`, `email`, `password`, `admin`, `superadmin`, `recovery`) VALUES (1, 'test', 'test@test.com', 'test', '0', '0', NULL);

# Clock in/out database set up
# Set @currenttime = current_timestamp();
#
# USE `TimeClock`;
# CREATE TABLE IF NOT EXISTS `clock` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `username` varchar(100) NOT NULL,
# `direction` varchar(4) NOT NULL,
# `location` varchar(100) NOT NULL,
# `time` varchar(255) NOT NULL,
# `servertime` varchar(255) NOT NULL,
# PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
# INSERT INTO `clock` (`id`, `username`, `direction`, `location`, `time`,`servertime`) VALUES (1, 'junleng', 'in', 'test', 'test', "@currenttime");


# Retrieves current time from a network time protocol
def ntp_time():
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    return ctime(response.tx_time)




# Code below does not retrieve sw.js (returns error)
# j = 'javascript'
# response=make_response(
#                  send_from_directory(current_app.send_static_file('sw.js'), mimetypes=j))
# #change the content header file. Can also omit; flask will handle correctly.
# response.headers['Content-Type'] = 'application/javascript'
# return response


# User Account Functions (Log In/ Log Out)

# Log user into application (Main Page, therefore '/')
@app.route('/', methods=['GET', 'POST'])
def log_in():
    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        macaddress = hex(uuid.getnode())
        
        query = text("SELECT * FROM users WHERE username='"+username+ "' AND password='"+ password+"'")
        engine = db.engine.execute(query)
        schema = UsersSchema(many=True)
        account = schema.dump(engine)
      
        if account:
            if macaddress == account[0]['macaddress']:
                session['username'] = request.form['username']
                return redirect(url_for('home'))
            else:
                msg = 'Device does not match original sign up device!'
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


# Log user out of application
@app.route('/logout', methods=['GET', 'POST'])
def log_out():
    session.clear()
    return redirect(url_for('log_in'))


# User sign up to create an account
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmPassword']
        macaddress = hex(uuid.getnode())
        
        query1 = text("SELECT * FROM users WHERE username = '"+username+"'")
        engine1 = db.engine.execute(query1)
        schema = UsersSchema(many=True)
        usernamedup =schema.dump(engine1)
        query2 = text("SELECT * FROM users WHERE email = '"+ email+"'")
        engine2 = db.engine.execute(query2)
        account = schema.dump(engine2)
        if usernamedup:
            msg = "Username is already in use !"
        elif account:
            msg = 'Email has already been registered with an account !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not password or not email:
            msg = 'Please fill out the form !'
        elif password != confirmpassword:
            msg = 'Passwords do not match!'
        else:
            insert_query = text("INSERT INTO users(username,email,password,macaddress,admin,superadmin,recovery) VALUES ({},{},{},{},0,0,NULL)".format("'"+username+"'", "'"+email+"'", "'"+password+"'", "'"+macaddress+"'"))
            engine = db.engine.execute(insert_query)
            msg = 'You have successfully registered !'

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg=msg)


# Gets an email from the user and sends a forget password email to them
@app.route('/forget', methods=['POST', 'GET'])
def forget():
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        
        query = text("SELECT * FROM users WHERE email='"+email+"'")
        engine = db.engine.execute(query)
        schema = UsersSchema(many=True)
        account = schema.dump(engine)
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not account:
            msg = 'Account does not exist!'
        else:
            # generates random 6 digit code --> send to email (will do tmr)
            digits = [i for i in range(0, 10)]
            random_str = ""
            for i in range(6):
                index = math.floor(random.random() * 10)
                random_str += str(digits[index])
           
            query2 = text("UPDATE users SET recovery ='"+random_str+"'"+" WHERE email='"+email+"'")
            db.engine.execute(query2)
            email = Message('Reset Password', sender='timeclockaktus@gmail.com', recipients=[email])
            email.html = "Dear,<br>" \
                         "Your recovery code to recover your password is " + random_str + ". You can recover your password here: http://127.0.0.1:5000/changepassword . <br>" \
                                                                                          "Yours sincerely, <br>" \
                                                                                          "TimeClock"
            mail.send(email)
            msg = "Email has been sent!"
            return redirect(url_for('change_password'))
    return render_template('forget.html', msg=msg)


# Displays page for user to change password (Recovery Code Portion)
@app.route('/changepassword', methods=['POST', 'GET'])
def change_password():
    msg = ''
    if request.method == 'POST':
       
        username = request.form['username']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        OTP = request.form['otpcode']
        query1 = text("SELECT * FROM users WHERE username = '"+username+"' AND recovery = '"+OTP+"'")
        engine1 = db.engine.execute(query1)
     
        
        if account == 1:
            if password == confirmPassword:
                query1 = text("SELECT * FROM users SET password = '"+password+" WHERE username = '"+username+"'")
                engine1 = db.engine.execute(query1)
               
                msg = 'Password has been changed!'
            elif password != confirmPassword:
                msg = 'Password does not match!'
        else:
            msg = 'Username/ OTP is incorrect!'
    return render_template('changepassword.html', msg=msg)



# Main user functions (Clock In/ Out)

@app.route('/home', methods=['POST', 'GET'])
# Displays home page (individual user clock in and all clock ins for admins)
def home():
    if request.method == 'POST':
        direction = request.form["direction"]
        location = request.form['address']
        time = request.form['timeclocked']
        if location != "" and time != "":
            username = session.get("username")
            servertime = str(ntp_time())
            insert_query = text("INSERT INTO clock(username,direction,location,time,servertime) VALUES ({},{},{},{},{})".format("'"+username+"'", "'"+direction+"'", "'"+location+"'", "'"+time+"'", "'"+servertime+"'"))
            engine = db.engine.execute(insert_query)
            msg = 'User successfully registered !'
            
            
            insert_query = text("INSERT INTO userview(username,direction,location,time,servertime) VALUES ({},{},{},{},{})".format("'"+username+"'", "'"+direction+"'", "'"+location+"'", "'"+time+"'", "'"+servertime+"'"))
            engine = db.engine.execute(insert_query)
            msg = 'Userview successfully registered !'

           
        else:
            pass
    username = session.get("username")
    query1 = text("SELECT * FROM userview WHERE username = '"+username+"' ORDER BY id DESC")
    selectQuery = db.engine.execute(query1)
    schema = UserViewSchema(many=True)
    data = schema.dump(selectQuery)
   
    # Data is clock in and clock out data and sAdmin checks if the user is a super admin and admin checks if the user is an admin
    return render_template('home.html', data=data, len=len(data))
    


# Delete user info from main admin page
@app.route('/delusertime/<int:id>', methods=['POST', 'GET'])
def delusertime(id):
    query1 = text("DELETE FROM userview WHERE id = '"+str(id)+"'")
    engine1 = db.engine.execute(query1)
   
    return redirect(url_for('home'))


@app.route('/about')
# Displays about page (Not completed)
def about_page():
    username = session.get("username")
   
    return render_template('about.html')




@app.route('/offline')
def offline():
    return app.send_static_file('offline.html')


@app.route('/service-worker')
def sw():
    return app.send_static_file('service-worker.js')


if __name__ == '__main__':
    app.run(debug=True)
