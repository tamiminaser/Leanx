from flask import Flask, render_template, redirect, session, url_for, request, flash
import MySQLdb
from flask_mysqldb import MySQL
import hashlib, uuid

app = Flask(__name__)

# Configure Flask app using config.py
app.config.from_object('config.Config')

# Making connection to MySQL database
db = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'userID' in session:
        return landing()
    else:
        return login()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userID' in session:
        return landing()
    if request.method == 'POST':
        if ('username' in request.form) and ('password' in request.form):
            username = request.form['username']
            password = request.form['password']
            # Now, let's define a cursor to execute command on our MySQL database
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM logininfo WHERE email=%s', [username])
            credentials = cursor.fetchone()
            if credentials is not None:
                if (credentials['email']==username):
                    hashed_password = credentials['password']
                    salt = credentials['salt']
                    if hashed_password == hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest():
                        session['userID'] = credentials['id']
                        return landing()
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
            cursor.execute('INSERT INTO logininfo (name, email, password, salt) VALUES (%s, %s, %s, %s)', (name, email, hashed_password, salt))
            db.connection.commit()
            return index()
    return render_template('register.html')

@app.route('/landing')
def landing():
    if 'userID' in session:
        return render_template('landing.html')
    else:
        return login()

@app.route('/logout')
def logout():
    session.pop('userID', None)
    return index()

if __name__ == '__main__':
    app.run(debug=True)
