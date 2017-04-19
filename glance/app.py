import os

from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory
import boto3

from packages.function import LoggedIn, CheckLoginDetails, upload_handler
from config  import cred


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

            f = request.files['file']
            filename = f.filename
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            boto3_session = boto3.session.Session(
                aws_access_key_id=cred.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=cred.AWS_SECRET_ACCESS_KEY,
            )

            s3 = boto3_session.resource('s3')

            data = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
            s3.Object(cred.AWS_BUCKET, filename).put(Body=open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb'))

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return render_template('uploadcomplete.html')
    else:
        return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=5000)
