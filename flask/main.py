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
    #return "<html><body>hi</body></html>"
    return render_template("index.html")

@app.route('/success')
def success():
    print(session['cache'])
    if session['logged_in'] and not (session['user'] == {}): return render_template("success.html")
    return redirect(url_for('index'))

@app.route('/logoff', methods=['POST'])
def logoff():
    session['logged_in'] = False
    session['user'] = {}
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    user = db.getUser(request.form['email'])
    if not user.exists:
        return redirect(url_for('index'))
    else:
        if bcrypt.check_password_hash(user.json['password'], request.form['password']):
            session['logged_in'] = True
            session['user'] = user.json
            del session['user']['password']
            session['cache'] = datetime.now()+timedelta(hours=8)
            
            print(session)
            
            return redirect(url_for('success'))
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
        print(session['user'])
        del session['user']['password']
        session['cache'] = datetime.now()+timedelta(hours=8)
        flash("You successfully registered.")
            
        return redirect(url_for('success'))

def main():
    return app.run('0.0.0.0')

if __name__ == '__main__': main()