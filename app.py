# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 10:11:12 2024

@author: patri
"""

from flask import Flask, render_template, request
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import os

app = Flask(__name__)

# Calculation function for payoff and savings
def calculate_payoff_and_savings(starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date):
    monthly_rate = interest_rate / 12 / 100
    
    # Calculate the original monthly payment for a 15-year fixed-rate loan
    initial_monthly_payment = starting_balance * (monthly_rate * (1 + monthly_rate)**(15*12)) / ((1 + monthly_rate)**(15*12) - 1)

    # Apply lump sum payment
    new_balance = current_balance - lump_sum

    if new_balance <= 0:
        return 0, 0, 0, datetime.now().year, datetime.now().month

    # New monthly payment after extra payment
    monthly_payment_with_extra = initial_monthly_payment + monthly_extra

    # Calculate new payoff period and total interest
    months = 0  # ✅ Initialize months to prevent NameError
    total_interest_new = 0
    while new_balance > 0:
        interest_for_month = new_balance * monthly_rate
        total_interest_new += interest_for_month
        principal_payment = monthly_payment_with_extra - interest_for_month

        if principal_payment <= 0:
            raise ValueError("Monthly payment is not sufficient to cover the interest. Increase the monthly extra payment.")

        if new_balance < principal_payment:
            principal_payment = new_balance
        
        new_balance -= principal_payment
        months += 1  # ✅ Ensure months increments correctly

    # ✅ Define years_remaining and months_remaining correctly
    years_remaining = months // 12  # Extract full years
    months_remaining = months % 12  # Extract remaining months

    # New payoff date
    new_payoff_date = datetime.now() + relativedelta(months=months)
    new_payoff_year = new_payoff_date.year
    new_payoff_month = new_payoff_date.month

    # Calculate original total interest up to today
    total_interest_old = 0
    old_balance = current_balance
    for _ in range(15 * 12):  # 180 months for a 15-year mortgage
        interest_for_month = old_balance * monthly_rate
        total_interest_old += interest_for_month
        principal_payment = initial_monthly_payment - interest_for_month
        old_balance -= principal_payment
        if old_balance <= 0:
            break

    total_interest_saved = total_interest_old - total_interest_new

    return years_remaining, months_remaining, total_interest_saved, new_payoff_year, new_payoff_month



@app.route('/', methods=['GET', 'POST'])
def index():
    defaults = {
        'starting_balance': 166500,
        'current_balance': 50163,
        'interest_rate': 3.25,
        'start_date': '2019-02-19'
    }

    if request.method == 'POST':
        try:
            starting_balance = float(request.form['starting_balance'])
            current_balance = float(request.form['current_balance'])
            interest_rate = float(request.form['interest_rate'])
            lump_sum = float(request.form['lump_sum']) if request.form['lump_sum'] else 0
            monthly_extra = float(request.form['monthly_extra']) if request.form['monthly_extra'] else 0

            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')

            # Run calculation function
            years_remaining, months_remaining, interest_saved, payoff_year, payoff_month = calculate_payoff_and_savings(
                starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date
            )


            return render_template(
                'index.html',
                result=True,
                years_remaining= years_remaining,  # ✅ Now matches HTML
                months_remaining= months_remaining,  # ✅ Now matches HTML
                interest_saved=interest_saved,
                payoff_year=payoff_year,
                payoff_month=payoff_month,
                defaults=defaults
            )
        except ValueError as e:
            return render_template('index.html', result=False, error=str(e), defaults=defaults)

    return render_template('index.html', result=False, defaults=defaults)

if __name__ == '__main__':
    app.run(debug=True)