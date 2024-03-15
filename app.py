from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-up', methods=('GET', 'POST'))
def set_up():
    if request.method == 'POST':
        url = request.form['sheet_URL']

        if not url:
            flash('Please enter the URL of your sheet')

        else:
            return redirect(url_for('index'))

    message = {
        'title': 'Message 1:',
        'content': 'Hello World!'
    }
    return render_template('set-up.html', message = message)