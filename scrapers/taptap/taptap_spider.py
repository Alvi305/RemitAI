import time
from datetime import datetime

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from scrapers.models.base_page import BasePage
from scrapers.utils.utils import setup_driver
from selenium.webdriver.support import expected_conditions as EC



class TapTapSpider:
    def __init__(self):
        self.driver = setup_driver(headless=True)
        self.driver.implicitly_wait(5)
        self.page = BasePage(self.driver)


    def scroll_down(self):
        send_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "origin-amount")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", send_input)
        time.sleep(1)

    def select_origin_currency(self):
        origin_select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "origin-currency")))
        origin_select.click()
        select = Select(origin_select)
        select.select_by_value("US-USD")
        # Alternative: origin_select.click(); origin_select.send_keys("US-USD"); origin_select.send_keys(Keys.ENTER)
        time.sleep(1)
        print("TapTap Selected US-USD")

    def send_amount(self, amount: str):
        amount_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "origin-amount")))
        amount_input.click()
        time.sleep(0.5)
        amount_input.clear()
        time.sleep(0.5)
        cleared_value = amount_input.get_attribute("value")
        # print(f"TapTap Value after clear(): {cleared_value}")
        actions = ActionChains(self.driver)
        actions.click(amount_input).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.DELETE).perform()
        time.sleep(1)
        amount_input.send_keys(amount)
        amount_input.send_keys(Keys.ENTER)
        time.sleep(1)

    def destination_currency(self):
        dest_select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "destination-currency")))
        dest_select.click()
        select = Select(dest_select)
        select.select_by_value("BD-BDT")
        # Alternative: dest_select.click(); dest_select.send_keys("BD-BDT"); dest_select.send_keys(Keys.ENTER)
        time.sleep(1)
        print("TapTap Selected BD-BDT")

    def receive_amount(self):
        received_amount = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "destination-amount")))
        received_amount.click()
        time.sleep(0.5)


    def extract_rate_fees(self):
        received_amount = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "destination-amount")))
        received_amount.click()
        time.sleep(0.5)
        receiving_value = received_amount.get_attribute("value")
        print(f"TapTap Receiving input value: {receiving_value}")

        rate_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "fxRateText")))
        exchange_rate = rate_element.text.strip()
        print(f"TapTap Exchange Rate: {exchange_rate}")

        fee_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "feeText")))
        fee_text = fee_element.text.strip()

        return exchange_rate,fee_text

    def scrape(self):
        self.driver.get("https://www.taptapsend.com/")

        self.scroll_down()

        self.select_origin_currency()

        self.destination_currency()

        self.send_amount("1000")

        exchange_rate,fee_text = self.extract_rate_fees()

        return {
            "exchange_rates": [{"pair": "USD/BDT", "rate": exchange_rate}],
            "transaction_fees": fee_text,
            "transfer_times": "2 days",
            "provider": {"name": "TapTapSend", "url": "https://www.taptapsend.com"},
            "timestamp": datetime.now().isoformat()
        }

    def close(self):
        self.driver.quit()
