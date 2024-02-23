from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def front_page():
    return render_template('front_page.html')

@app.route('/org/job')
def org_job_open():
    return render_template('org_job_open.html')

@app.route('/org/login')
def org_login():
    return render_template('org_login.html')

@app.route('/org/register')
def org_register():
    return render_template('org_register.html')

@app.route('/org/view')
def org_view():
    return render_template('org_view.html')

@app.route('/vol/login')
def vol_login():
    return render_template('vol_login.html')

@app.route('/vol/register')
def vol_register():
    return render_template('vol_register.html')

@app.route('/vol/skill')
def vol_skill_selection():
    return render_template('vol_skill_selection.html')

@app.route('/vol/view')
def vol_view():
    return render_template('vol_view.html')

if __name__ == '__main__':
    app.run(debug=True)
