from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import email_validator


app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nikhilgolla76'
app.config['MYSQL_DB'] = 'my_flask_app_db'
import os


secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key

mysql = MySQL(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id,email):
        self.id = user_id
        self.email = email


    def get_id(self):
        return str(self.id)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(min=4, max=29)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Login')

from wtforms import IntegerField
class RegistrationForm(FlaskForm):
    username = StringField("Your Name", validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=8, max=80)])
    age = IntegerField('Age', validators=[InputRequired()])
    sex = StringField('Sex', validators=[InputRequired()])
    languages = StringField('Languages', validators=[InputRequired()])
    submit = SubmitField('Register')


class OrgLoginForm(FlaskForm):
    name = StringField('Organization Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Login')

class OrgRegistrationForm(FlaskForm):
    name = StringField('Organization Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=8, max=80)])
    type = StringField('Organization Type', validators=[InputRequired()])
    submit = SubmitField('Register')

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user_id = user_data[0]
        email = user_data[1]
        return User(user_id, email)
    else:
        return None



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        conn = mysql.connection  # Use mysql.connection instead of mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            if user[3] == password:
                # Assuming user[0] contains the user ID
                print("success")
                user_id = user[0]
                login_user(User(user_id,email), remember=True)
                return render_template('vol_skill_selection.html')
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('User not found. Please try again or register.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')

def commmon():
    return render_template('commonpage.html')
@app.route('/vol_skill_selection.html')
def index():
    email = current_user.email if current_user.is_authenticated else None
    return render_template('vol_skill_selection.html')  # Make sure it renders index.html


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed.")  # Check if the route is accessed
    print("Form data received:", request.form)
    form = RegistrationForm() # Retrieve languages from the form
        
    email = form.email.data
    username = form.username.data
    password = form.password.data
    age = form.age.data
    sex = form.sex.data
    languages = form.languages.data  # Retrieve languages from the form
    print("em")

    print("hello")
    conn = mysql.connection
    print("Connection object:", conn)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
            flash('Email already exists. Please choose a different email.', 'danger')
    else:
           try:
                print("Hi")
                insert_query = "INSERT INTO User (username, email, password, age, sex, languages) VALUES (%s, %s, %s, %s, %s, %s)"
                print("Insert query:", insert_query)
                print("Data:", (username, email, password, age, sex, languages))
                cursor.execute(insert_query, (username, email, password, age, sex, languages))
                conn.commit()
                print("Number of rows affected:", cursor.rowcount)
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('login'))
           except Exception as e:
                print("Error during database insertion:", e)
                flash('An error occurred. Please try again.', 'danger')

    

    return render_template('register.html', form=form)



@app.route('/org_login', methods=['GET', 'POST'])
def org_login():
    form = OrgLoginForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Organization WHERE name = %s", (name,))
        org = cursor.fetchone()
        if org:
            if org[2] == password:
                return redirect(url_for('org_dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('Organization not found. Please try again or register.', 'danger')
    return render_template('org_login.html', form=form)

@app.route('/org_register', methods=['GET', 'POST'])
def org_register():
    form = OrgRegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        org_type = form.type.data
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Organization WHERE name = %s", (name,))
        existing_org = cursor.fetchone()
        if existing_org:
            flash('Organization name already exists. Please choose a different name.', 'danger')
        else:
            cursor.execute("INSERT INTO Organization (name, email, password, type) VALUES (%s, %s, %s, %s)", (name, email, password, org_type))
            conn.commit()
            flash('Organization registered successfully. Please log in.', 'success')
            return redirect(url_for('org_login'))
    return render_template('org_register.html', form=form)

@app.route('/org_dashboard')
@login_required
def org_dashboard():
    return render_template('org_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
