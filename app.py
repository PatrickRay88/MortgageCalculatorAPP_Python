from flask import Flask, render_template, request
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

def calculate_payoff_and_savings(starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date, loan_term):
    """ Calculates new payoff date and interest savings """

    monthly_rate = interest_rate / 12 / 100
    total_months = loan_term * 12

    # Compute Original Monthly Payment for the Full Loan Term
    initial_monthly_payment = starting_balance * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)

    # Compute Original Interest If No Extra Payments Are Made
    original_balance = current_balance
    total_interest_original = 0
    months_left = 0

    while original_balance > 0:
        interest_for_month = original_balance * monthly_rate
        total_interest_original += interest_for_month
        principal_payment = initial_monthly_payment - interest_for_month

        if original_balance < principal_payment:
            principal_payment = original_balance

        original_balance -= principal_payment
        months_left += 1

    # Apply Lump Sum Payment (if any)
    new_balance = current_balance - lump_sum

    if new_balance <= 0:
        return 0, 0, 0, datetime.now().year, datetime.now().month

    # Compute New Monthly Payment With Extra Payments
    monthly_payment_with_extra = initial_monthly_payment + monthly_extra
    months_paid = 0
    total_interest_new = 0

    while new_balance > 0:
        interest_for_month = new_balance * monthly_rate
        total_interest_new += interest_for_month
        principal_payment = monthly_payment_with_extra - interest_for_month

        if principal_payment <= 0:
            raise ValueError("Monthly payment is too low. Increase extra payments.")

        if new_balance < principal_payment:
            principal_payment = new_balance

        new_balance -= principal_payment
        months_paid += 1

    new_payoff_date = datetime.now() + relativedelta(months=months_paid)

    today = datetime.now()
    total_remaining_months = (new_payoff_date.year - today.year) * 12 + (new_payoff_date.month - today.month)
    
    years_remaining = total_remaining_months // 12
    months_remaining = total_remaining_months % 12

    # 🔹 **Fix: Ensure Total Interest Saved is Only Calculated If Extra Payments Exist**
    if lump_sum > 0 or monthly_extra > 0:
        total_interest_saved = total_interest_original - total_interest_new
    else:
        total_interest_saved = 0  # No savings if no extra payments

    return years_remaining, months_remaining, total_interest_saved, new_payoff_date.year, new_payoff_date.month


@app.route('/', methods=['GET', 'POST'])
def index():
    defaults = {
        'starting_balance': 166500,
        'current_balance': 59500,
        'interest_rate': 3.25,
        'start_date': '2019-02-19',
        'loan_term': 15
    }

    if request.method == 'POST':
        try:
            starting_balance = float(request.form['starting_balance'])
            current_balance = float(request.form['current_balance'])
            interest_rate = float(request.form['interest_rate'])
            lump_sum = float(request.form['lump_sum']) if request.form['lump_sum'] else 0
            monthly_extra = float(request.form['monthly_extra']) if request.form['monthly_extra'] else 0
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')

            loan_term = int(request.form['loan_term']) if 'loan_term' in request.form else 15

            years_remaining, months_remaining, interest_saved, payoff_year, payoff_month = calculate_payoff_and_savings(
                starting_balance, current_balance, interest_rate, lump_sum, monthly_extra, start_date, loan_term
            )

            return render_template('index.html', result=True, years_remaining=years_remaining, months_remaining=months_remaining, interest_saved=interest_saved, payoff_year=payoff_year, payoff_month=payoff_month, defaults={**defaults, 'loan_term': loan_term})
        except ValueError as e:
            return render_template('index.html', result=False, error=str(e), defaults=defaults)

    return render_template('index.html', result=False, defaults=defaults)


if __name__ == '__main__':
    app.run(debug=True)
