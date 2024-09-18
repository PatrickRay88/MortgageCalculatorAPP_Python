import unittest
from app import app  # Import your Flask app

class MortgageAppTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client using the Flask application configured for testing
        self.app = app.test_client()
        self.app.testing = True  # Propagates exceptions to the test client

    def test_calculate_mortgage_with_range(self):
        # Define the constant form inputs (these values won't change in the test loop)
        form_data_template = {
            'starting_balance': '166500',
            'current_balance': '76000',
            'interest_rate': '3.25',
            'lump_sum': '0',
            'start_date': '2019-02-01'
        }

        # Loop through different extra monthly principal amounts from 100 to 1500 in increments of 100
        for monthly_extra in range(100, 1600, 100):
            # Update the form data with the current monthly_extra value
            form_data = form_data_template.copy()  # Copy the template
            form_data['monthly_extra'] = str(monthly_extra)  # Set the monthly extra payment

            # Send a POST request to the '/' route with the form data
            response = self.app.post('/', data=form_data)

            # Check if the request was successful (status code 200)
            self.assertEqual(response.status_code, 200)

            # Print out the monthly_extra amount being tested
            print(f"\nTesting with Monthly Extra Payment: ${monthly_extra}")

            # Print out the New Payoff Date and Total Interest Saved from the response
            data = response.data.decode('utf-8')

            # Extract and print the New Payoff Date and Total Interest Saved
            start = data.find("New Payoff Date:")
            end = data.find("Total Interest Saved:")
            if start != -1 and end != -1:
                new_payoff_date = data[start:end].strip()
                total_interest_saved = data[end:].strip()

                print(new_payoff_date)
                print(total_interest_saved)

if __name__ == '__main__':
    unittest.main()