from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha256_crypt
from rq import Queue
from redis import Redis
from mail import send_mail

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

redis_conn = Redis()
q = Queue(connection=redis_conn)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(35), unique=True, nullable=False)
    username = db.Column(db.String(35), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __str__(self):
        return f'<User {self.username}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)

class RegistrationForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35), validators.Email(), validators.InputRequired()])
    username = StringField('Имя пользователя', [validators.Length(min=4, max=35), validators.InputRequired()])
    password = PasswordField('Пароль', [validators.Length(min=8, max=35), validators.InputRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Ещё раз пароль')

class LoginForm(Form):
    username = StringField('Имя пользователя', [validators.InputRequired()])
    password = PasswordField('Пароль', [validators.InputRequired()])

class FeedbackForm(Form):
    title = StringField('Тема', [validators.InputRequired()])
    text = TextAreaField('Подробности')

    
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = 'Войдите, чтобы отправить заявку'
login_manager.login_message_category = 'danger'

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        text = form.text.data

        feedback = Feedback(user_id=current_user.id, title=title, text=text)
        db.session.add(feedback)
        db.session.commit()

        q.enqueue(send_mail, args=(title, text))

        flash('Заявка отправлена. Спасибо', category='success')

        return redirect(url_for('index'))

    return render_template('feedback.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        hashed_password = sha256_crypt.encrypt(form.password.data)
        user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Вы успешно зарегистрировались', category='success')
        return redirect(url_for('feedback'))
    
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()

        if user and sha256_crypt.verify(form.password.data, user.password):
            login_user(user)
            flash('Вы успешно вошли', category='success')
            return redirect(url_for('feedback'))
        else:
            flash('Неверное имя пользователя или пароль', category='danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли', category='success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
