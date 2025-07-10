import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
from scrapers.models.base_page import BasePage
from scrapers.utils.utils import setup_driver


class WiseSpider:
    def __init__(self):
        self.driver = setup_driver(headless=True)
        self.driver.implicitly_wait(5)
        self.page = BasePage(self.driver)

    def select_currency(self, currency: str, button_id: str, search_id: str):
        button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, button_id))
        )
        button.click()
        input_currency_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, search_id))
        )
        input_currency_field.send_keys(currency)
        input_currency_field.send_keys(Keys.ENTER)

    def input_amount(self, amount: float):
        input_field_selected = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"input#source"))
        )
        actions = ActionChains(self.driver)
        actions.click(input_field_selected).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.DELETE).perform()
        input_field_selected.send_keys(amount)


    def extract_exchange_rate(self) -> str:
        exchange_rate_button = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-describedby='rateLabel']"))
        )
        return exchange_rate_button.text.strip()

    def extract_transaction_fees(self) -> str:
        fees_container = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".Fees_container"))
        )
        fees_html = fees_container.get_attribute("outerHTML")
        soup = BeautifulSoup(fees_html, "html.parser")
        individual_fees = []

        # Extract individual fees
        fee_items = soup.select("ul li.Fees_row")
        for item in fee_items:
            fee_name = item.select_one("div:first-child span").text.strip()
            fee_amount = item.select_one("div:last-child span").text.strip()
            individual_fees.append(f"{fee_name}: {fee_amount}")

        # Extract total fees
        total_fees_row = soup.select_one("div.Fees_row:last-child")
        percentage_fee = total_fees_row.select_one("strong:first-child span").text.strip()
        percentage_value = re.search(r'(\d+\.\d+%)', percentage_fee).group(1) if re.search(r'(\d+\.\d+%)', percentage_fee) else "Unknown"
        flat_fee = total_fees_row.select_one("strong:last-child span").text.strip()

        return f" Total: {flat_fee}, Percentage: {percentage_value}"

    def extract_transfer_time(self) -> str:
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".np-section.m-t-2"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".np-section.m-t-2 p.m-b-0 strong"))
        )
        transfer_time_container = self.driver.find_element(By.CSS_SELECTOR, ".tapestry-card-content .np-section.m-t-2 span[role='status']")
        transfer_time_html = transfer_time_container.get_attribute("outerHTML")
        soup = BeautifulSoup(transfer_time_html, "html.parser")
        transfer_time = soup.select_one("p.m-b-0 strong").text.strip()
        return transfer_time.replace("by ", "")



    def scrape(self):
        """Scrape Wise data for USD to BDT with 1000 amount."""
        self.driver.get("https://www.wise.com/")

        # Select currencies
        self.select_currency("USD", "sourceSelectedCurrency", "sourceSelectedCurrencySearch")
        self.select_currency("BDT", "targetSelectedCurrency", "targetSelectedCurrencySearch")

        # Input amount
        self.input_amount(1000)

        # Extract data
        time.sleep(5)  # delay for UI stability
        exchange_rate = self.extract_exchange_rate()
        transaction_fees = self.extract_transaction_fees()
        transfer_time = self.extract_transfer_time()

        return {
            "exchange_rates": [{"pair": "USD/BDT", "rate": exchange_rate}],
            "transaction_fees": transaction_fees,
            "transfer_times": transfer_time,
            "provider": {"name": "Wise", "url": "https://wise.com"},
            "timestamp": datetime.now().isoformat()
        }

    def close(self):
        self.driver.quit()
