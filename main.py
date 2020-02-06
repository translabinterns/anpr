import pymysql
from app import app
from db_config import mysql
from flask import flash, session, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

@app.route('/')
def index():
    if 'email' in session:
        username = session['email']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to logout</a></b>" + \
               "<p><button type='submit'>Run Program</button></p>"

    return redirect('/login')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/submit', methods=['POST'])
def login_submit():
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    # validate the received values
    if _email and _password:
        # check user exists
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM tbl_user WHERE user_email=%s"
        sql_where = (_email,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            test = hashlib.md5()
            test.update(_password.encode('utf-8'))
            if(test.hexdigest()==row[3]):
                session['email'] = row[1]
                cursor.close()
                conn.close()
                return redirect('/')
            # if check_password_hash(row[3], _password.decode('utf-8')):
            #     session['email'] = row[1]
            #     cursor.close()
            #     conn.close()
            #     return redirect('/')
            else:
                flash('Invalid password!')
                return redirect('/login')
        else:
            flash('Invalid email/password!')
            return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(port=5001)