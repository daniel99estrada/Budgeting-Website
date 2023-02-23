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

@app.route('/add_expense', methods=['POST'])
def add_expense():
    type = request.form['expense-income']
    name = request.form['name']
    cost = request.form['cost']
    category = request.form['category']
    # new_category = request.form['new_category']
    date_str = request.form['date']
    date_str = request.form['date']

    if not date_str:
        today = date.today()
        date_str = today.strftime('%Y-%m-%d')

    # if new_category:
    #     category = new_category

    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    if type == 'income':
        income = Income(source=name, value=cost, date=date_obj)
        db.session.add(income)
    else:
        expense = Expense(name=name, cost=cost, category=category, date=date_obj)
        db.session.add(expense)

    db.session.commit()
    
    categories = list(set(expense.category for expense in Expense.query.all()))

    return render_template('add_expense.html', categories=list(categories))

@app.route('/display')
def display():
    # get expenses with the selected category
    selected_category = request.form.get('category')
    
    expenses = Expense.query.filter_by(category=selected_category).all()
    total = sum(expense.cost for expense in expenses)

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
    return render_template('display_data.html',chart_file=chart_file, expenses=expenses, incomes=incomes)



@app.route('/', methods=['GET', 'POST'])
def index():

    categories = list(set(expense.category for expense in Expense.query.all()))
    return render_template('add_expense.html', categories=list(categories))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





