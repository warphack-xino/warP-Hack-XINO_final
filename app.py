from flask import *
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meaningoflife=47'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()  
login_manager.init_app(app)
login_manager.login_view = 'login'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    price = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"{self.id}. {self.name} - { self.price } NouCredits"

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField(validators=[InputRequired(), Length(min=4, max=32)])
    password = PasswordField( validators=[InputRequired(), Length(min=8, max=80)])


class User(UserMixin, db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    balance = db.Column(db.Integer, default=100)
    notes = db.relationship('Note', backref='user')

class Note(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

bandage = Product(id=1, name="Bandages", price=10)
food_packet = Product(id=2, name="Food packets", price=20)
water = Product(id=3, name="Water", price=5)
ors = Product(id=4, name="Oral Rehydration Solution", price=15)
jacket = Product(id=5, name="Jackets", price=20)
medicine = Product(id=6, name="General medicines", price=15)
helmet = Product(id=7, name="Helmet", price=20)
climbing_ropes = Product(id=8, name="Climbing ropes", price=5)
backpack = Product(id=9, name="Backpack", price=20)
binoculars = Product(id=10, name="Binoculars", price=20)


@app.route('/emergency', methods=['GET', 'POST'])
@login_required
def emergency():
    if request.method == 'POST':
        note = request.form.get('note')
        desc = request.form.get('desc')
        new_note = Note(title=note, desc=desc,user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
    note_num = note = request.form.get('note')
    return render_template("nos.html", user=current_user, num=note_num)


@app.route("/emergency/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Note.query.filter_by(sno=sno).first()
        todo.title=title 
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect('/emergency')
    todo = Note.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

@app.route("/emergency/delete/<int:sno>")
def delete(sno):
    todo = Note.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/emergency")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/')
            
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect('/')

    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/essentials', methods=['GET', 'POST'])
def essentials():
        return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars)

@app.route('/buy', methods=['GET', 'POST'])
@login_required 
def buy():
    creds = current_user.balance  
    balance = creds - bandage.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)
    
@app.route('/buy2', methods=['GET', 'POST'])
@login_required 
def buy2():
    creds = current_user.balance  
    balance = creds - food_packet.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy3', methods=['GET', 'POST'])
@login_required 
def buy3():
    creds = current_user.balance  
    balance = creds - water.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)

@app.route('/buy4', methods=['GET', 'POST'])
@login_required 
def buy4():
    creds = current_user.balance  
    balance = creds - ors.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy5', methods=['GET', 'POST'])
@login_required 
def buy5():
    creds = current_user.balance  
    balance = creds - jacket.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy6', methods=['GET', 'POST'])
@login_required 
def buy6():
    creds = current_user.balance  
    balance = creds - medicine.price
    
    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy7', methods=['GET', 'POST'])
@login_required 
def buy7():
    creds = current_user.balance  
    balance = creds - helmet.price

    
    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy8', methods=['GET', 'POST'])
@login_required 
def buy8():
    creds = current_user.balance  
    balance = creds - climbing_ropes.price

    
    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy9', methods=['GET', 'POST'])
@login_required 
def buy9():
    creds = current_user.balance  
    balance = creds - backpack.price

    
    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)


@app.route('/buy10', methods=['GET', 'POST'])
@login_required 
def buy10():
    creds = current_user.balance  
    balance = creds - binoculars.price

    return render_template('essentials.html', bandage=bandage, food_packet=food_packet, water=water, ors=ors, jacket=jacket, medicine=medicine, helmet=helmet, climbing_ropes=climbing_ropes, backpack=backpack, binoculars=binoculars, creds=balance)

@app.route('/credits')
@login_required
def credits():
    return render_template('credits.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=False)