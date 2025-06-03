from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


def setup_drivver(headless=True):
    options =  Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
    driver = WebDriver(options=options)
    return driver
