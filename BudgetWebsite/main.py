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

@app.route('/add_expense', methods=['POST'])
def add_expense():
    name = request.form['name']
    cost = request.form['cost']
    category = request.form['category']
    new_category = request.form['new_category']
    date_str = request.form['date']

    if not date_str:
        today = date.today()
        date_str = today.strftime('%Y-%m-%d')

    if new_category:
        category = new_category

    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    expense = Expense(name=name, cost=cost, category=category, date=date_obj)
    db.session.add(expense)
    db.session.commit()

    return 'Expense added!'

@app.route('/expenses')
def list_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses)


from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
def index():
    # Get the selected category and date range from the form
    selected_category = request.form.get('category')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    # Parse the start and end dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

    # Get the expenses that match the selected category and date range
    if selected_category:
        expenses = Expense.query.filter_by(category=selected_category)
    else:
        expenses = Expense.query

    if start_date:
        expenses = expenses.filter(Expense.date >= start_date)

    if end_date:
        expenses = expenses.filter(Expense.date <= end_date)

    expenses = expenses.all()

    # Calculate the total cost of the expenses
    total = sum(expense.cost for expense in expenses)

    # Get the list of categories and today's date
    categories = ['food', 'rent', 'entertainment']
    today = date.today().strftime('%Y-%m-%d')

    # Get the sum of expenses for each category
    data = []

    for category in categories:
        expenses_by_category = Expense.query.filter_by(category=category)

        if start_date:
            expenses_by_category = expenses_by_category.filter(Expense.date >= start_date)

        if end_date:
            expenses_by_category = expenses_by_category.filter(Expense.date <= end_date)

        total_by_category = sum(expense.cost for expense in expenses_by_category)
        data.append(total_by_category)

    # Display the data in a bar chart
    fig, ax = plt.subplots()
    ax.bar(categories, data)
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
        ax.bar(categories, data)
        ax.set_xlabel('Category')
        ax.set_ylabel('Total Cost')
        ax.set_title('Expenses by Category')
        plt.savefig(chart_file)

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('add_expense.html', categories=list(categories), today=today, chart_file=chart_file, expenses=expenses)




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
