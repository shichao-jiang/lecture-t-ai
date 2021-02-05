from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from transcribe_gcloud import transcribe
import string, random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
#app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///penis.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:harshil@35.202.242.209/main'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    password_hash = db.Column(db.String(256))
    code = db.Column(db.String(64))
    ended = db.Column(db.Integer)
    def __repr__(self):
        return username

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(256))
    code = db.Column(db.String(64), index = True, unique = True)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Re-enter Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Create Account")

class JoinForm(FlaskForm):
    code = StringField("Code", validators=[DataRequired()])
    submit = SubmitField("Join Class")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/audio', methods=['POST'])
@login_required
def audio():
    with open('./file.webm', 'wb') as file:
        file.write(request.data)
    questions = transcribe()
    for question in questions: 
        newquestion = Question(text=question, code=current_user.code)
        db.session.add(newquestion)
    db.session.commit()
    return "questions"

@app.route('/send', methods=['POST'])
@login_required
def send():
    user = User.query.get(current_user.id)
    user.ended = 1
    db.session.commit()
    return "success"

@app.route('/start', methods=['POST'])
@login_required
def start():
    user = User.query.get(current_user.id)
    user.ended = 0
    Question.query.filter_by(code=current_user.code).delete()
    db.session.commit()
    return "deleted"

@app.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    form = JoinForm()
    if form.validate_on_submit():
        session['classcode'] = form.code.data
        return redirect(url_for('questions', _external=True, _scheme='http'))        


    return render_template('student.html', form=JoinForm())

@app.route('/questions', methods=['GET'])
def questions():
    code = session.get('classcode')
    questions = []
    if code:
        questions = Question.query.filter_by(code=code).all()
    else:
        return redirect(url_for('student', _external=True, _scheme='http'))

    return render_template('questions.html', questions=questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):  
            login_user(user)
            return redirect(url_for('home', _external=True, _scheme='http'))
        else:
            error = "invalid credentials"
    else:
        flash(form.errors)

    return render_template('login.html', users=User.query.all(), form=LoginForm(), error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).count() > 0:
            error = "User already exists"
        else:
            try:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                db.session.add(User(username=form.username.data, password_hash=generate_password_hash(form.password.data), code=code, ended=0))
                db.session.commit()
            except:
                db.session.rollback()
    else:
        flash(form.errors)

    return render_template('register.html', users=User.query.all(), form=RegisterForm(), error=error)
    
if __name__ == "__main__": 
    app.run()