from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)
mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ACH025",
    database="expense_tracker"
)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('index'))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("Username already exits", "error")
        return redirect(url_for('signup'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    mysql.commit()

    flash("Signup successful! Please login.", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' in session:
        cursor = mysql.cursor(dictionary=True)
        cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('index.html', username=user['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Validate and convert inputs
            salary = float(request.form['salary'])
            food_expenses = float(request.form['food_expenses'])
            travel_expenses = float(request.form['travel_expenses'])
            accommodation = float(request.form['accommodation'])
            other_expenses = float(request.form['other_expenses'])
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')

            # Ensure values are non-negative
            if salary < 0 or food_expenses < 0 or travel_expenses < 0 or accommodation < 0 or other_expenses < 0:
                raise ValueError("Expenses and salary must be non-negative.")

            total_expenses = food_expenses + travel_expenses + accommodation + other_expenses
            savings = salary - total_expenses

            if total_expenses > salary:
                flash("Invalid expenses. Total expenses cannot be greater than salary.", "error")
                return redirect(url_for('add_expense'))

            cursor = mysql.cursor(dictionary=True)
            cursor.execute("SELECT * FROM expenses WHERE user_id = %s AND MONTH(date) = %s AND YEAR(date) = %s",
                           (session['user_id'], date.month, date.year))
            existing_expenses = cursor.fetchall()

            if existing_expenses:
                return render_template('confirm_update.html', expenses=existing_expenses)

            cursor.execute("INSERT INTO expenses (user_id, salary, food_expenses, travel_expenses, accommodation, other_expenses, date, savings) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (session['user_id'], salary, food_expenses, travel_expenses, accommodation, other_expenses, date, savings))
            mysql.commit()
            flash("Expenses added successfully!", "success")
            return redirect(url_for('view_expense'))

        except ValueError as e:
            flash(f"Invalid input: {e}", "error")
            return redirect(url_for('add_expense'))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('add_expense'))
    else:
        return render_template('addexpense.html')

@app.route('/visualization')
def visualization():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('visualization.html')

@app.route('/get_expenses')
def get_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    expenses = cursor.fetchall()
    return jsonify(expenses)

@app.route('/view_expense')
def view_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    expenses = cursor.fetchall()
    return render_template('viewexpense.html', expenses=expenses)

@app.route('/update_expense', methods=['POST'])
def update_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        salary = float(request.form['salary'])
        food_expenses = float(request.form['food_expenses'])
        travel_expenses = float(request.form['travel_expenses'])
        accommodation = float(request.form['accommodation'])
        other_expenses = float(request.form['other_expenses'])

        # Check if any of the expense values are negative
        if any(amount < 0 for amount in [salary, food_expenses, travel_expenses, accommodation, other_expenses]):
            flash("Expense values cannot be negative.", "error")
            return redirect(request.referrer)

        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        total_expenses = food_expenses + travel_expenses + accommodation + other_expenses
        savings = salary - total_expenses
        expense_id = int(request.form['expense_id'])

        cursor = mysql.cursor(dictionary=True)
        cursor.execute("UPDATE expenses SET salary = %s, food_expenses = %s, travel_expenses = %s, accommodation = %s, other_expenses = %s, savings = %s WHERE id = %s",
                       (salary, food_expenses, travel_expenses, accommodation, other_expenses, savings, expense_id))
        mysql.commit()
        flash("Expenses updated successfully!", "success")
        return redirect(url_for('view_expense'))
    except ValueError:
        flash("Invalid expense values. Please enter valid numeric values.", "error")
        return redirect(request.referrer)
    except Exception as e:
        flash(f"Error updating expenses: {e}", "error")
        return redirect(request.referrer)


@app.route('/planning', methods=['GET', 'POST'])
def planning():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        try:
            salary = float(request.form['salary'])
            desired_savings = float(request.form['savings'])

            # Check if any of the values are negative
            if salary < 0 or desired_savings < 0:
                flash("Salary and savings values cannot be negative.", "error")
                return redirect(url_for('planning'))

            # Check if desired savings is greater than salary
            if desired_savings >= salary:
                flash("Desired savings should be less than the salary.", "error")
                return redirect(url_for('planning'))

            cursor = mysql.cursor(dictionary=True)
            cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC LIMIT 3", (user_id,))
            last_three_months_expenses = cursor.fetchall()

            if len(last_three_months_expenses) < 3:
                flash("Please enter at least 3 months of expenses data to use the planning feature.", "error")
                return redirect(url_for('add_expense'))

            # Convert all necessary fields to float
            total_food = sum(float(expense['food_expenses']) for expense in last_three_months_expenses)
            total_travel = sum(float(expense['travel_expenses']) for expense in last_three_months_expenses)
            total_accommodation = sum(float(expense['accommodation']) for expense in last_three_months_expenses)
            total_other = sum(float(expense['other_expenses']) for expense in last_three_months_expenses)
            total_expenses = total_food + total_travel + total_accommodation + total_other

            avg_food = total_food / total_expenses
            avg_travel = total_travel / total_expenses
            avg_accommodation = total_accommodation / total_expenses
            avg_other = total_other / total_expenses

            remaining_amount = salary - desired_savings

            # Ensure remaining_amount is a float
            remaining_amount = float(remaining_amount)

            # Perform budget calculations and round off the results
            food_budget = round(remaining_amount * avg_food, 2)
            travel_budget = round(remaining_amount * avg_travel, 2)
            accommodation_budget = round(remaining_amount * avg_accommodation, 2)
            other_budget = round(remaining_amount * avg_other, 2)

            return render_template('planning_result.html', 
                                   salary=round(salary, 2), 
                                   savings=round(desired_savings, 2), 
                                   food_budget=food_budget, 
                                   travel_budget=travel_budget, 
                                   accommodation_budget=accommodation_budget, 
                                   other_budget=other_budget)
        except ValueError:
            flash("Invalid input. Please enter valid numeric values for salary and savings.", "error")
            return redirect(url_for('planning'))

    return render_template('planning.html')


@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get the expense_id from the form submission
    expense_id = request.form['expense_id']

    # Connect to the database
    cursor = mysql.cursor()

    try:
        # Delete the expense from the database
        cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, session['user_id']))
        mysql.commit()
        flash("Expense deleted successfully!", "success")
    except mysql.connector.Error as err:
        # Handle database errors
        flash(f"Error deleting expense: {err}", "error")

    # Redirect back to the view_expense page
    return redirect(url_for('view_expense'))


if __name__ == '__main__':
    app.run(debug=True)
