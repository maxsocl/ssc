#! /usr/bin/env python2.7

# TODO ADD login feature
# TODO ADD Database intergation (sqlite3) - display last action with related user
# TODO ADD form for construction LOGIN_NAME
# TODO ADD Execution delSession ONLY after listSession
# TODO Correct output session information
# TODO avoid company specific

import socket
import sqlite3


from flask import Flask, render_template, request


DATABASE = '/tmp/webclient.db'
SECRET_KEY = 'develop key'

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('main.html')


@app.route("/help/")
def help():
    return render_template('help.html')


@app.route('/delsession/', methods=['GET', 'POST'])
def delsession():
    if request.method == 'POST' and not request.form['login_name'].isspace() and \
       (request.form['listSession'] == 'list' or request.form['listSession'] == 'del'):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '172.16.0.1'
        port = 000000

        try:
            s.connect((host, port))
        except Exception as e:
            return render_template('form.html', result=str(e))

        else:
            login_name = request.form['login_name']
            user = 'user'
            s.send(user)
            response = s.recv(64)

            if response == 'ok':
                s.send(login_name)
                if s.recv(8) == 'ok':
                    s.send(request.form['listSession'])
                msg = s.recv(1024)
                s.close()
                return render_template('form.html', result=msg)
            else:
                return render_template('form.html', result=response)
    else:
        return render_template('form.html', result='')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port = 80, debug=True)