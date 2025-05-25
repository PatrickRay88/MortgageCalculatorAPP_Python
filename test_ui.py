import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class MortgageAppUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        import time
        selenium_url = os.environ.get('SELENIUM_REMOTE_URL')
        if selenium_url:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            cls.driver = webdriver.Remote(
                command_executor=selenium_url,
                options=options
            )
            # Wait for Flask app to be up before proceeding
            for _ in range(10):
                try:
                    cls.driver.get('http://127.0.0.1:5000/')
                    if 'Mortgage Payoff Calculator' in cls.driver.page_source:
                        break
                except Exception:
                    time.sleep(1)
            else:
                raise RuntimeError('Flask app did not start in time for Selenium test.')
        else:
            cls.driver = webdriver.Chrome()
            cls.driver.get('http://127.0.0.1:5000/')

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_modal_popup_and_save(self):
        driver = self.driver
        # Fill out the form
        driver.find_element(By.ID, 'starting_balance').clear()
        driver.find_element(By.ID, 'starting_balance').send_keys('100000')
        driver.find_element(By.ID, 'current_balance').clear()
        driver.find_element(By.ID, 'current_balance').send_keys('50000')
        driver.find_element(By.ID, 'interest_rate').clear()
        driver.find_element(By.ID, 'interest_rate').send_keys('3.5')
        driver.find_element(By.ID, 'lump_sum').clear()
        driver.find_element(By.ID, 'lump_sum').send_keys('1000')
        driver.find_element(By.ID, 'monthly_extra').clear()
        driver.find_element(By.ID, 'monthly_extra').send_keys('200')
        # Set the date using JavaScript for reliability
        driver.execute_script("document.getElementById('start_date').value = '2018-01-01';")
        # Submit the form
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        # Wait for modal (increase timeout to 20s)
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'resultsModal'))
            )
        except Exception as e:
            driver.save_screenshot('selenium_failure.png')
            raise e
        # Check modal content
        modal = driver.find_element(By.ID, 'resultsModal')
        self.assertIn('Results', modal.text)
        self.assertIn('New Payoff Date', modal.text)
        # Test Save button (file download is browser-handled, so we check button presence)
        save_btn = driver.find_element(By.ID, 'saveResultsBtn')
        self.assertTrue(save_btn.is_displayed())
        # Optionally, click OK to close
        ok_btn = driver.find_element(By.CSS_SELECTOR, '.btn-secondary[data-dismiss="modal"]')
        ok_btn.click()
        time.sleep(1)

if __name__ == '__main__':
    unittest.main()
