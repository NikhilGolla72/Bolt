from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import InputRequired, Length, Email
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import email_validator
import pymysql
import pandas as pd

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
    postal_code = IntegerField('Postal Code', validators=[InputRequired()])  # Add postal code field
    languages = StringField('Languages')
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
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            if user[3] == password:
                user_id = user[0]
                login_user(User(user_id, email), remember=True)
                return redirect(url_for('vol_skill_selection'))  # Redirect to the skill selection page
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
    languages_str = request.form.get('languages')
    if languages_str:
        languages = languages_str.split(',')
    postal_code=form.postal_code.data
    # Retrieve languages from the form
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
                languages_str = ', '.join(languages)
                insert_query = "INSERT INTO User (username, email, password, age, sex, languages,postal_code) VALUES (%s, %s, %s, %s, %s, %s,%s)"
                print("Insert query:", insert_query)
                print("Data:", (username, email, password, age, sex, languages,postal_code))
                cursor.execute(insert_query, (username, email, password, age, sex, languages_str,postal_code))
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



class VolSkillSelectionForm(FlaskForm):
    skill_1 = StringField('Skill 1', validators=[InputRequired()])
    skill_2 = StringField('Skill 2', validators=[InputRequired()])
    skill_3 = StringField('Skill 3', validators=[InputRequired()])
    skill_4 = StringField('Skill 4', validators=[InputRequired()])
    submit = SubmitField('Submit')

@app.route('/vol_skill_selection', methods=['GET', 'POST'])
@login_required
def vol_skill_selection():
    if current_user.is_authenticated:
        form = VolSkillSelectionForm()
        print("1")
        if form.validate_on_submit():
            print("2")
            skills = [form.skill_1.data, form.skill_2.data, form.skill_3.data, form.skill_4.data]
            save_skills_to_database(skills)
            flash('Skills saved successfully!', 'success')
            return redirect(url_for('vol_view'))
        return render_template('vol_skill_selection.html', form=form)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))


def save_skills_to_database(skills):
    try:
        conn = mysql.connection
        with conn.cursor() as cursor:
            # Convert the list of skills into a comma-separated string
            skills_str = ', '.join(skills)
            user_id = current_user.id
            # Update the 'skills' column for the current user
            cursor.execute("UPDATE User SET skills = %s WHERE id = %s", (skills_str, user_id))
        conn.commit()
    except Exception as e:
        print("Error saving skills to database:", e)
    finally:
        conn.close()

@app.route('/submit_skills', methods=['POST'])
@login_required  # Ensure the user is logged in
def submit_skills():
    if request.method == 'POST':
        # Extract the selected skills from the form data
        selected_skills = request.form.getlist('selectedSkills')
        
        # Process the selected skills (e.g., save them to the database)
        save_skills_to_database(selected_skills)
        
        # Optionally, render a success page or redirect the user
        flash('Skills saved successfully!', 'success')
        return redirect(url_for('vol_view'))



from flask import render_template
import pandas as pd
import ast


class VolInterestSelectionForm(FlaskForm):
    interest_1 = StringField('Interest 1')
    interest_2 = StringField('Interest 2')
    interest_3 = StringField('Interest 3')
    interest_4 = StringField('Interest 4')
    submit = SubmitField('Submit')
    
def save_interests_to_database(interests):
    try:
        conn = mysql.connection
        with conn.cursor() as cursor:
            # Convert the list of interests into a comma-separated string
            interests_str = ', '.join(interests)
            user_id = current_user.id
            # Update the 'interests' column for the current user
            cursor.execute("UPDATE User SET interests = %s WHERE id = %s", (interests_str, user_id))
        conn.commit()
    except Exception as e:
        print("Error saving interests to database:", e)
    finally:
        conn.close()
@app.route('/submit_interests', methods=['POST'])
@login_required  # Ensure the user is logged in
def submit_interests():
    if request.method == 'POST':
        # Extract the selected skills from the form data
        selected_skills = request.form.getlist('selectedSkills')
        
        # Process the selected skills (e.g., save them to the database)
        save_skills_to_database(selected_skills)
        
        # Extract the selected interests from the form data
        selected_interests = request.form.getlist('selectedInterests')
        
        # Process the selected interests (e.g., save them to the database)
        save_interests_to_database(selected_interests)
        
        return redirect(url_for('success_page'))




job_data = pd.read_csv('Experiment\data\job_volunteer_openings_50_records.csv')
person_data = pd.read_csv('C:\\Users\\golla\\OneDrive\\Desktop\\python\\Experiment\\data\\person_data_500_records_with_names.csv')


def append_person_data(user_data):
    file_path='C:\\Users\\golla\\OneDrive\\Desktop\\python\\Experiment\\data\\person_data_500_records_with_names.csv'
    with open(file_path, 'a') as f:
        f.write(','.join(map(str, user_data.values())) + '\n')   
        
def run_algorithm(new_person_index, new_skills):
    matching_results = []

    # Load job data (assuming job_data is already defined)
    for index, job in job_data.iterrows():
        match_score = calculate_match_score(person_data.iloc[new_person_index], job)
        matching_results.append({"Person Index": new_person_index, "Job Index": index, "Match Score": match_score})

    matching_results.sort(key=lambda x: x['Match Score'], reverse=True)
    return matching_results


def compare_pin_codes(pin1, pin2):
    num1 = int(str(pin1)[:3])
    num2 = int(str(pin2)[:3])
    difference = abs(num1 - num2)
    if difference >= 201:
        return 0
    elif 101 <= difference <= 200:
        return 1
    elif 51 <= difference <= 100:
        return 2
    elif 11 <= difference <= 50:
        return 3
    elif 0 <= difference <= 10:
        return 4

def calculate_match_score(person, job):
    shared_skills = set(person['Skills']).intersection(set(job['Skills Requirement']))
    shared_languages = set(person['Languages']).intersection(set(job['Language Requirement']))
    min_age, max_age = map(int, job['Age Range'].split('-'))
    if not shared_skills or not (min_age <= person['Age'] <= max_age) or len(shared_languages) == 0:
        return 0
    score = len(shared_languages) + (3 if job['Interest'].lower() in [interest.lower() for interest in person['Interests']] else 0) + len(shared_skills) * 2
    score += compare_pin_codes(person['Postal Code'], job['PIN Code'])
    return score
import pymysql

def fetch_user_data_from_database(host, user, password, database):
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            # Fetch required user data from the database
            cursor.execute("SELECT username, age, skills, languages, interests, postal_code FROM User ORDER BY id DESC LIMIT 1")
            user_data = cursor.fetchone()

            if user_data:
                # Deserialize the languages field into a list
                languages_str = user_data['languages']
                user_data['languages'] = languages_str.split(', ')

            return user_data
    finally:
        connection.close()



user_data = fetch_user_data_from_database('127.0.0.1', 'root', 'Nikhilgolla76', 'my_flask_app_db')


if user_data:
    # Append the user's data to the person.csv file
    append_person_data(user_data)
    new_person_index = person_data.shape[0] - 1
 # Assuming the last row is the newly added person
    new_skills = user_data['skills'].split(',')  # Assuming skills are stored as a comma-separated string in the database
    matching_results = run_algorithm(new_person_index, new_skills)
    print(matching_results)  # Display matching results for the new person index
else:
    print("No user data found.")


if __name__ == '__main__':
    app.run(debug=True)
