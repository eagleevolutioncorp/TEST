from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from wtforms.fields import IntegerField, StringField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
admin = Admin(app, name='Carfax Panamá', template_mode='bootstrap3')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

class VehicleView(ModelView):
    form_overrides = {
        'plate': StringField,
        'make': StringField,
        'model': StringField,
        'year': IntegerField,
        'accidents': IntegerField,
        'owners': IntegerField
    }

    form_args = {
        'plate': {'label': 'License Plate'},
        'make': {'label': 'Make'},
        'model': {'label': 'Model'},
        'year': {'label': 'Year'},
        'accidents': {'label': 'Accidents'},
        'owners': {'label': 'Owners'}
    }

    form_create_rules = ['plate', 'make', 'model', 'year', 'accidents', 'owners']
    form_edit_rules = form_create_rules

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin.add_view(VehicleView(Vehicle, db.session))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = AdminUser.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['POST'])
def report():
    plate = request.form['plate']
    vehicle = Vehicle.query.filter_by(plate=plate).first()
    return render_template('report.html', report=vehicle)

with app.app_context():
    db.create_all()
    if not Vehicle.query.first():
        vehicles = [
            Vehicle(plate='AB1234', make='Toyota', model='Corolla', year=2020, accidents=0, owners=1),
            Vehicle(plate='CD5678', make='Honda', model='Civic', year=2019, accidents=1, owners=2),
            Vehicle(plate='EF9012', make='Ford', model='Fusion', year=2018, accidents=0, owners=1)
        ]
        db.session.bulk_save_objects(vehicles)
        db.session.commit()

    if not AdminUser.query.filter_by(username='admin').first():
        db.session.add(AdminUser(username='admin', password='admin123'))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)

