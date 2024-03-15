import requests
import json
from flask import Flask, render_template


api_key = "AIzaSyDm3NkpUP7s2-9eIctdLS2OZzcYKWnVvXc"
api_url = "https://sheets.googleapis.com/v4/spreadsheets/1SMhSsePT-WJPna2oq5NnE2zyIVSOZycV9kEgkWHcNfs/values/Sheet1!A1:D5?key=" + api_key


class MockDBRow:

    def __init__(self, s, n, c):
        self.street = s
        self.name = n
        self.city = c


    def get_street(self):
        return self.__street


    def get_name(self):
        return self.__name


    def get_city(self):
        return self.__city



app = Flask(__name__)

@app.route('/')
def home():
    raw = requests.get(api_url)
    print (raw)
    rows = raw.json()['values']
    print(rows)
    
    return render_template('Grid.html', rows = rows)


