import os
from flask import Flask, render_template, redirect, session, url_for, request, flash
import MySQLdb
from flask_mysqldb import MySQL
import hashlib, uuid
import random

app = Flask(__name__)
app.config['UPLOAD_PATH'] = './static/img/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jfif']

# Configure Flask app using config.py
app.config.from_object('config.Config')

# Making connection to MySQL database
db = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'userID' in session:
        return redirect(url_for('landing'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userID' in session:
        return  redirect(url_for('landing'))
    if request.method == 'POST':
        if ('username' in request.form) and ('password' in request.form):
            username = request.form['username']
            password = request.form['password']
            # Now, let's define a cursor to execute command on our MySQL database
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM login WHERE email=%s', [username])
            credentials = cursor.fetchone()
            if credentials is not None:
                if (credentials['email']==username):
                    hashed_password = credentials['password']
                    salt = credentials['salt']
                    if hashed_password == hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest():
                        session['userID'] = credentials['id']
                        session['name'] = credentials['name']
                        cursor.execute('SELECT * FROM profile WHERE user_id=%s', [credentials['id']])
                        profile = cursor.fetchone()
                        session['profile_pic'] = profile['profile_pic']
                        session['occupation'] = profile['occupation']
                        session['location'] = profile['location']
                        session['email'] = profile['email']

                        return redirect(url_for('landing')) 
                    else:
                        return 'Unsuccessful Login'
                else:
                    return 'Unsuccessful Login'
            else:
                return 'Unsuccessful Login'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'name' in request.form and 'email' in request.form and 'password' in request.form:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
            # Now, let's define a cursor to execute command on our MySQL database
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO login (name, email, password, salt) VALUES (%s, %s, %s, %s)', (name, email, hashed_password, salt))
            db.connection.commit()
            cursor.execute('SELECT id FROM login WHERE email=%s AND password=%s', (email, hashed_password))
            user_id = cursor.fetchone()['id']
            cursor.execute('INSERT INTO profile (user_id, name, email) VALUES (%s, %s, %s)', (user_id, name, email))
            db.connection.commit()
            return  redirect(url_for('index'))
    return render_template('register.html')

def refresh_profile_info():
    if 'userID' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT name, email, profile_pic, occupation, location FROM profile WHERE user_id = %s', [session['userID']])
        profile_info = cursor.fetchone()
        session['name'] = profile_info['name']
        session['email'] = profile_info['email']
        session['profile_pic'] = profile_info['profile_pic']
        session['occupation'] = profile_info['occupation']
        session['location'] = profile_info['location']

@app.route('/landing')
def landing():
    if 'userID' in session:
        refresh_profile_info()
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT profile.name, profile.profile_pic, messages.message, messages.time_stamp FROM messages JOIN profile ON messages.user_id = profile.user_id;')
        messages = cursor.fetchall()
        data = {'name': session['name'], 
                'profile_pic': session['profile_pic'],
                'occupation': session['occupation'],
                'location': session['location'], 
                'email': session['email'],
                'messages': messages}
        return render_template('landing.html', data=data)
    else:
        return redirect(url_for('index'))

@app.route('/landing', methods=['POST'])
def posting():
    if 'userID' in session:
        if request.method == 'POST':
            user_id = session['userID']
            message = request.form['message']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO messages (user_id,message) VALUES (%s, %s)', (user_id, message))
            db.connection.commit()
        return redirect(url_for('landing'))
    else:
        return redirect(url_for('index'))

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/settings', methods=['POST'])
def upload_and_record():
    if 'userID' in session:
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        user_id = session['userID']
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            _, image_file_extension = os.path.splitext(uploaded_file.filename)
            img_filename = str(random.getrandbits(64))+image_file_extension
            img_path = 'img/'+img_filename
            uploaded_file.save('./static/'+img_path)
            cursor.execute('UPDATE profile SET profile_pic = %s WHERE user_id = %s', (img_path, user_id))
            db.connection.commit()
        location = request.form['location']
        occupation = request.form['occupation']
        cursor.execute('UPDATE profile SET location = %s, occupation = %s WHERE user_id = %s', (location, occupation, user_id))
        db.connection.commit()
    return redirect(url_for('landing'))


@app.route('/logout')
def logout():
    session.pop('userID', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    session.clear()
    # Comment or uncomment based on whether you need dev mode or prod mode.
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
