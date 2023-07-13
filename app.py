from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee.db'

db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.String(10))
    employee_type = db.Column(db.String(50))
    wages = db.relationship('Wage', backref='employee', lazy=True)

    def __init__(self, name, age, employee_type):
        self.name = name
        self.age = age
        self.employee_type = employee_type


class Wage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    wage = db.Column(db.Float)
    week_start = db.Column(db.Date)
    working_hours = db.Column(db.Float)

    def __init__(self, employee_id, wage, week_start, working_hours):
        self.employee_id = employee_id
        self.wage = wage
        self.week_start = week_start
        self.working_hours = working_hours




# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        employee_type = request.form['employee_type']
        employee = Employee(name=name, age=age, employee_type=employee_type)
        db.session.add(employee)
        db.session.commit()
        return redirect(url_for('employees'))
    return render_template('register.html')


@app.route('/employees')
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)


@app.route('/wages')
def wages():
    wage_records = Wage.query.join(Employee).all()
    return render_template('wages.html', wage_records=wage_records)

from datetime import datetime, timedelta

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    employees = Employee.query.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'POST':
        employee_id = request.form['employee_id']

        # Calculate the start date of the week
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        for day in range(7):
            in_time = request.form.get(f'in_time_{day}')
            out_time = request.form.get(f'out_time_{day}')

            if in_time and out_time:
                # Calculate the working hours
                in_time_dt = datetime.strptime(in_time, '%H:%M')
                out_time_dt = datetime.strptime(out_time, '%H:%M')
                working_hours = (out_time_dt - in_time_dt).total_seconds() / 3600

                # Retrieve the employee details and wage based on employee type and age
                employee = Employee.query.get(employee_id)
                employee_type = employee.employee_type
                age = employee.age

                # Calculate the wage based on employee type, age, and working hours
                if employee_type == 'NI':
                    if age == 'Below 23':
                        wage = 10.18
                    else:
                        wage = 10.42
                elif employee_type == 'CashIN':
                    wage = 6
                elif employee_type == 'Ni&CashIn':
                    if age == 'Below 23':
                        if working_hours > 20:
                            wage = 10.18 * 20 + 6 * (working_hours - 20)
                        else:
                            wage = 10.42 * working_hours
                    else:
                        if working_hours > 20:
                            wage = 10.42 * 20 + 6 * (working_hours - 20)
                        else:
                            wage = 10.42 * working_hours

                # Save the wage information to the database
                wage_entry = Wage(employee_id=employee_id, wage=wage, week_start=week_start,
                                  working_hours=working_hours)
                db.session.add(wage_entry)

        db.session.commit()
        return redirect(url_for('attendance'))

    return render_template('attendance.html', employees=employees, days=days)



if __name__ == '__main__':
    app.run(debug=True)
