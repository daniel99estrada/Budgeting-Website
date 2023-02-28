from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import matplotlib.pyplot as plt
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    type = request.form['type']
    name = request.form['name']
    cost = request.form['cost']
    category = request.form.get('category')
    other_category = request.form.get('other_category')
    date_str = request.form['date']

    if not date_str:
        today = date.today()
        date_str = today.strftime('%Y-%m-%d')

    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    if category == 'other':
        category = other_category

    # category = "boom"

    if type == 'income':
        income = Income(source=category, value=cost, date=date_obj)
        db.session.add(income)
    else:
        expense = Expense(name=name, cost=cost, category=category, date=date_obj)
        db.session.add(expense)

    db.session.commit()
    
    categories = list(set(expense.category for expense in Expense.query.all()))

    return render_template('add_expense.html', categories=list(categories))

@app.route('/display')
def display():
    expenses = sum(expense.cost for expense in Expense.query.all()) 
    income = sum(income.value for income in Income.query.all()) 

    savings = abs(income - expenses)
    sizes = [savings, expenses]
    labels = ["Savings", "Expenses"]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct=lambda p: '{:.0f}%'.format(p * income / 100))

    # Save the pie chart to a PNG file
    pieChartFile = 'static/pieChart.png'
    plt.savefig(pieChartFile)

    # Get the list of categories from the database
    categories = list(set(expense.category for expense in Expense.query.all()))

    # Get the sum of expenses for each category
    totalCosts = []
    for category in categories:
        expenses = Expense.query.filter_by(category=category)
        total = sum(expense.cost for expense in expenses)
        totalCosts.append(total)

    # Display the data in a bar chart
    fig, ax = plt.subplots()
    ax.bar(categories, totalCosts)
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Cost')
    ax.set_title('Expenses by Category')

    # Save the chart to a PNG file
    chart_file = 'static/chart.png'
    plt.savefig(chart_file)

    # Check if the chart file already exists
    if not os.path.exists(chart_file):
        # Generate the chart and save it to the file
        fig, ax = plt.subplots()
        ax.bar(categories, totalCosts)
        ax.set_xlabel('Category')
        ax.set_ylabel('Total Cost')
        ax.set_title('Expenses by Category')
        plt.savefig(chart_file)

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    incomes = Income.query.order_by(Income.date.desc()).all()
    return render_template('display_data.html',chart_file=chart_file, pieChartFile=pieChartFile, expenses=expenses, incomes=incomes)



@app.route('/', methods=['GET', 'POST'])
def index():

    categories = list(set(expense.category for expense in Expense.query.all()))
    return render_template('add_expense.html', categories=list(categories))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





