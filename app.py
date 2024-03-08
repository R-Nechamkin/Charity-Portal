from flask import Flask, render_template

@app.route('/')
def home():
    rows = [10,5,2]
    return render_template('Grid.html', rows = rows)
