import re
import time
from datetime import datetime


from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from scrapers.models.base_page import BasePage
from scrapers.utils.utils import setup_driver


class XoomSpider:
    def __init__(self):
        self.driver = setup_driver(headless=True)
        self.driver.implicitly_wait(5)
        self.page = BasePage(self.driver)


    def accept_cookies(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)

        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='cookie-accept']"))  # Adjust selector
            )
            self.driver.execute_script("arguments[0].click();", cookie_button)
            print("Dismissed cookie banner")
        except:
            pass

    def send_amount(self, amount: str):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_1y4lgjacz"))
        )
        time.sleep(1)

        amount_input_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input-amount-sending"))
        )
        amount_input_field.click()
        time.sleep(0.5)

        amount_input_field.clear()
        time.sleep(0.5)
        cleared_value = amount_input_field.get_attribute("value")
        print(f"Value after clear(): {cleared_value}")

        actions = ActionChains(self.driver)
        actions.click(amount_input_field).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.DELETE).perform()
        time.sleep(1)

        # Enter amount
        amount_input_field.send_keys(amount)
        amount_input_field.send_keys(Keys.ENTER)

        # print("Successfully entered 1000 USD") # TODO : Remove in final production code

        time.sleep(1)

    def receive_amount(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_1y4lgjacy"))
        )

        received_amount = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input-amount-receiving"))
        )
        received_amount.click()
        time.sleep(0.5)

        receiving_value = received_amount.get_attribute("value")
        # print(f"Receiving input value: {receiving_value}") # TODO : Remove in final production code

    def extract_rate_fees(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_1y4lgjacz"))
        )

        # Navigate to the specific container with classes "_1y4lgjacy _1y4lgjafj _1y4lgja79 _1mcye514"
        rate_container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div._1y4lgjacy._1y4lgjafj._1y4lgja79._1mcye514")
            )
        )

        rate_element = rate_container.find_element(
            By.CSS_SELECTOR, "p._18ax91o1._18ax91o0._1mcye512"
        )
        exchange_rate = rate_element.text
        # print(f"Exchange Rate: {exchange_rate}") # TODO : Remove in final production code

        fee_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "xoom_fees_info"))
        )
        self.driver.execute_script("arguments[0].click();", fee_button)
        time.sleep(1)

        # Extract PYUSD transaction fee
        pyusd_fee = 0.0
        fee_containers = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div._1y4lgjacz._1y4lgjad0")
            )
        )

        fees = []
        for container in fee_containers:
            try:
                fee_element = container.find_element(
                    By.CSS_SELECTOR, "p._18ax91o1._18ax91o0"
                )
                fee_text = fee_element.text.strip()
                try:
                    fee_value = float(fee_text)
                    fees.append(fee_value)
                except ValueError:
                    continue
            except:
                continue

        # Find and print the minimum fee
        min_fee = min(fees) if fees else 0.0
        min_fee_str = f"Total: {min_fee:.2f} USD"
        # print(f"Transaction Fee: {min_fee} USD") # TODO : Remove in final production code
        return exchange_rate, min_fee_str

    def scrape(self):
        self.driver.get("https://www.xoom.com/en-us/usd/send-money/transfer?countryCode=BD")

        # Accept cookies
        self.accept_cookies()

        # Input amount (1000 USD)
        self.send_amount("1000")

        # Retrieve receiving amount
        self.receive_amount()

        # Extract rate and fee
        exchange_rate, min_fee = self.extract_rate_fees()

        # Parse exchange rate to extract numeric part as string
        rate_match = re.search(r"1 USD = ([\d.]+) BDT", exchange_rate)
        exchange_rate_value = rate_match.group(1) if rate_match else "0.0"


        return {
            "exchange_rates": [{"pair": "USD/BDT", "rate": exchange_rate}],
            "transaction_fees": min_fee,
            "transfer_times": "2 days",
            "provider": {"name": "Xoom", "url": "https://www.xoom.com"},
            "timestamp": datetime.now().isoformat()
        }

    def close(self):
        self.driver.quit()