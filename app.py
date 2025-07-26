from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    accidents = db.Column(db.Integer, default=0)
    owners = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Vehicle {self.plate}>'

with app.app_context():
    db.create_all()
    # Add some dummy data if the db is empty
    if not Vehicle.query.first():
        vehicles = [
            Vehicle(plate='AB1234', make='Toyota', model='Corolla', year=2020, accidents=0, owners=1),
            Vehicle(plate='CD5678', make='Honda', model='Civic', year=2019, accidents=1, owners=2),
            Vehicle(plate='EF9012', make='Ford', model='Fusion', year=2018, accidents=0, owners=1)
        ]
        db.session.bulk_save_objects(vehicles)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['POST'])
def report():
    plate = request.form['plate']
    vehicle = Vehicle.query.filter_by(plate=plate).first()
    return render_template('report.html', report=vehicle)

if __name__ == '__main__':
    app.run(debug=True)
