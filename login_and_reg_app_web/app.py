import requests
from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="service_db",
                        user="postgres",
                        password="1234",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('login'):
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                return render_template('login.html', message='Заполните обязательные поля')

            cursor.execute('SELECT * FROM service.users WHERE login=%s AND password=%s', (str(username), str(password)))
            records = list(cursor.fetchall())

            if not records:
                return render_template('login.html', message='Такой комбинации логина и пароля не существует')

            return render_template('account.html', full_name=records[0][1], login=login, password=password)
        elif request.form.get('registration'):
            return redirect('/registration')
    return render_template('login.html')


@app.route('/registration/', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        login = request.form.get('login')
        password = request.form.get('password')

        if not name or not login or not password:
            return render_template('registration.html', message='Заполните все поля')

        cursor.execute('SELECT * FROM service.users WHERE login=%s ', (str(login), ))
        records = list(cursor.fetchall())
        if records:
            return render_template('registration.html', message='Пользователь с таким логином уже существует')

        cursor.execute('INSERT INTO service.users (full_name, login, password) VALUES (%s, %s, %s);',
                       (str(name), str(login), str(password)))

        conn.commit()
        return redirect('/login/')

    return render_template('registration.html')
