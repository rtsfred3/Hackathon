from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import re

import database

NAME_MATCH = re.compile(r'.[^1-9\s]*')
EMAIL_MATCH = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = "a"
bcrypt = Bcrypt(app)

db = database.database()

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/sendScore', methods=['POST'])
def sendScore():
    if request.method == 'POST' and session['logged_in']:
        query = "INSERT INTO dailyscore (user_id, score) VALUES (%(user_id)s, %(score)s);"
        data = {
            'user_id': session['user']['id'],
            'score': request.form['score']
        }
        db.query_db(query, data)
        session['user']['scores'].append(int(request.form['score']))
        return "{'status':200}", 200
    else:
        return "{'status':418, 'error':'not logged in'}", 418

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

@app.route('/activity')
def activity():
    return render_template("activity.html")

@app.route('/socialevents')
def socialevents():
    return render_template("SocialEvents.html")

@app.route('/prequestionnare')
def prequestionnare():
    return render_template("Prequestionnare.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/resources')
def resources():
    return render_template("resources.html")

@app.route('/success')
def success():
    if session['logged_in'] and not (session['user'] == {}): return render_template("success.html")
    return redirect(url_for('index'))

@app.route('/logoff', methods=['POST'])
def logoff():
    session['logged_in'] = False
    session['user'] = {}
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    user = db.getUser(request.form['email'])
    if not user.exists:
        return redirect(url_for('index'))
    else:
        if bcrypt.check_password_hash(user.json['password'], request.form['password']):
            session['logged_in'] = True
            session['user'] = user.json
            del session['user']['password']
            session['cache'] = datetime.now()+timedelta(hours=8)
            
            return redirect(url_for('prequestionnare'))
        else:
            session['logged_in'] = False
            session['user'] = {}
            
            return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    if len(request.form['name']) < 3 or len(request.form['email']) < 1 or len(request.form['password']) < 1 or len(request.form['confirm_password']) < 1 or request.form['password'] != request.form['confirm_password'] or (not EMAIL_MATCH.match(request.form['email']) and len(request.form['email']) > 0) or (len(request.form['password']) > 0 and len(request.form['password']) < 8 and request.form['password'] == request.form['confirm_password']):
        if len(request.form['email']) < 1:
            flash("Email cannot be empty!")
        
        if len(request.form['name']) < 1:
            flash("Name cannot be empty!")
        elif len(request.form['name']) <= 2:
            flash("Name must be more than two letters!")
        
        if len(request.form['password']) < 1:
            flash("Password cannot be empty!")
        
        if len(request.form['confirm_password']) < 1:
            flash("Confirm Password cannot be empty!")
        
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords do not match!")
        
        if not EMAIL_MATCH.match(request.form['email']) and len(request.form['email']) > 0:
            flash("Invalid Email Address!")
        
        if len(request.form['password']) > 0 and len(request.form['password']) < 8 and request.form['password'] == request.form['confirm_password']:
            flash("Password does not meet the minimum length of 8 characters!")
        
        return redirect(url_for('index'))
    else:
        query = "INSERT INTO users (name, email, password) VALUES (%(name)s, %(email)s, %(password)s);"
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        }
        db.query_db(query, data)
        
        user = db.getUser(request.form['email'])
        
        session['logged_in'] = True
        session['user'] = user.json
        del session['user']['password']
        session['cache'] = datetime.now()+timedelta(hours=8)
        flash("You successfully registered.")
            
        return redirect(url_for('success'))

def main():
    return app.run('0.0.0.0')

if __name__ == '__main__': main()