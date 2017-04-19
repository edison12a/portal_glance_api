import os

from flask import Flask, flash, redirect, render_template, request, session, abort

from packages.function import LoggedIn, CheckLoginDetails, upload_handler


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/tmp')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    if LoggedIn(session):
        return render_template('home.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        form = request.form

        data = {
            'username': form['username'],
            'password': form['password']
        }

        if CheckLoginDetails(**data):
            session['logged_in'] = True
        else:
            # TODO: Something here?
            pass

    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False

    return home()


@app.route('/upload')
def upload():
    if LoggedIn(session):
        return render_template('upload.html')
    else:
        return home()


@app.route('/uploading', methods=['POST'])
def uploading():
    if LoggedIn(session):
        if request.method == 'POST':

            file = request.files['file']
            upload_handler(file, app.config['UPLOAD_FOLDER'])

            return render_template('uploadcomplete.html')
    else:
        return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=5000)
