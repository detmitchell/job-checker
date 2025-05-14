from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SFE_USERNAME, SFE_PASSWORD
from logger import logger

def login(driver):
    """Log in to the PowerSchool SFE portal."""
    driver.get("https://ignite.sfe.powerschool.com/logOnInitAction.do")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "userId")))
    driver.find_element(By.ID, "userId").send_keys(SFE_USERNAME)
    driver.find_element(By.ID, "userPin").send_keys(SFE_PASSWORD)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "submitBtn"))).click()
    logger.info("🔐 Logged in successfully.")
