# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 10:11:12 2024

@author: patri
"""

from flask import Flask, render_template, request
from datetime import datetime
from dateutil.relativedelta import relativedelta  # <-- UPDATED: Added this import for accurate date calculation
import math

app = Flask(__name__)

def calculate_payoff_and_savings(starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date):
    monthly_rate = interest_rate / 12 / 100
    
    # Calculate the original monthly payment assuming a 15-year fixed-rate loan
    initial_monthly_payment = starting_balance * (monthly_rate * (1 + monthly_rate)**(15*12)) / ((1 + monthly_rate)**(15*12) - 1)

    # Apply lump sum payment to the current balance (from today onward)
    new_balance = current_balance - lump_sum

    if new_balance <= 0:
        # If the lump sum completely pays off the mortgage
        return 0, 0, 0, datetime.now().year, datetime.now().month

    # New monthly payment after adding the extra monthly amount (applied only from today onward)
    monthly_payment_with_extra = initial_monthly_payment + monthly_extra

    # Calculate new payoff period (months) from today onward
    months = 0
    total_interest_new = 0

    while new_balance > 0:
        # Calculate interest for the month
        interest_for_month = new_balance * monthly_rate
        total_interest_new += interest_for_month
        principal_payment = monthly_payment_with_extra - interest_for_month

        if principal_payment <= 0:
            raise ValueError("Monthly payment is not sufficient to cover the interest. Increase the monthly extra payment.")

        # Make sure we don't overpay the balance
        if new_balance < principal_payment:
            principal_payment = new_balance  # Reduce the final payment to exactly pay off the loan
        
        # Update the balance after paying principal
        new_balance -= principal_payment
        months += 1

    # Calculate the new payoff date based on the months calculated, starting from today
    new_payoff_date = datetime.now() + relativedelta(months=months)
    new_payoff_year = new_payoff_date.year
    new_payoff_month = new_payoff_date.month

    # Calculate the original total interest paid for the 15-year loan up to today
    total_interest_old = 0
    old_balance = current_balance
    for _ in range(15 * 12):  # 180 months for a 15-year mortgage
        interest_for_month = old_balance * monthly_rate
        total_interest_old += interest_for_month
        principal_payment = initial_monthly_payment - interest_for_month
        old_balance -= principal_payment
        if old_balance <= 0:
            break

    # Calculate total interest saved by comparing original vs new total interest
    total_interest_saved = total_interest_old - total_interest_new

    # Return years, months, interest saved, and new payoff date
    years = months // 12
    remaining_months = months % 12

    return years, remaining_months, total_interest_saved, new_payoff_year, new_payoff_month

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            starting_balance = float(request.form['starting_balance'])
            current_balance = float(request.form['current_balance'])
            interest_rate = float(request.form['interest_rate'])
            lump_sum = float(request.form['lump_sum'])
            monthly_extra = float(request.form['monthly_extra'])
            
            # Convert start_date from form to datetime
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')  # Ensure this field is being passed

            # Call the function with the correct arguments, including start_date
            years, remaining_months, interest_saved, payoff_year, payoff_month = calculate_payoff_and_savings(
                starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date
            )

            return render_template('index.html', 
                                   result=True, 
                                   years=years, 
                                   remaining_months=remaining_months, 
                                   interest_saved=interest_saved, 
                                   payoff_year=payoff_year, 
                                   payoff_month=payoff_month)
        except ValueError as e:
            return render_template('index.html', result=False, error=str(e))

    return render_template('index.html', result=False)

if __name__ == '__main__':
    app.run(debug=True)