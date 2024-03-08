from flask import Flask, render_template


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
    rows = [MockDBRow('Crescent', 'Rivka', 'bang'),
            MockDBRow('Plastic', 'Devora', 'Passaic')
            ]
            
    return render_template('Grid.html', rows = rows)


