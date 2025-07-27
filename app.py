import os
from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Configuración básica
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Base de datos
db = SQLAlchemy(app)

# Modelo de ejemplo
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10))
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.String(10))
    accidents = db.Column(db.String(100))
    owners = db.Column(db.String(100))

# Login
login_manager = LoginManager(app)

class User(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    return User()

# Vista personalizada de admin
class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Admin
admin = Admin(app, name='CarFax Panama', index_view=SecureAdminIndexView(), template_mode='bootstrap3')
admin.add_view(SecureModelView(Vehicle, db.session))

# Rutas
@app.route('/')
def home():
    return 'Bienvenido a CarFax Panamá. <a href="/admin">Ir al Admin</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv('ADMIN_PASSWORD', 'admin123'):
            login_user(User())
            return redirect('/admin')
        else:
            error = 'Contraseña incorrecta.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# Inicializar DB si no existe
@app.before_first_request
def create_tables():
    db.create_all()

# Run local (ignorado por gunicorn en producción)
if __name__ == '__main__':
    app.run(debug=True)

