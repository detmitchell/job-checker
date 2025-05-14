import time
import platform
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger

FILTER_TIME_TO_WAIT = 15

def format_date(date):
    """Format date depending on OS (Windows vs Unix)."""
    return date.strftime("%#m/%#d/%y") if platform.system() == "Windows" else date.strftime("%-m/%-d/%y")

def apply_date_filter(driver):
    """Apply a date range filter to show all jobs up to 10 years out."""
    try:
        start = datetime.today()
        end = start + timedelta(days=3650)

        start_str = format_date(start)
        end_str = format_date(end)

        logger.info(f"📅 Start: {start_str}, End: {end_str}")

        logger.info("🔘 Clicking 'Date' filter label...")
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "date-filter-label"))).click()

        logger.info("🎯 Selecting 'Date Range' radio button...")
        radios = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pds-radio-button-widget"))
        )
        for label in radios:
            if label.text.strip() == "Date Range":
                label.click()
                logger.info("✅ Clicked 'Date Range'.")
                break
        else:
            logger.warning("❌ 'Date Range' radio label not found.")

        logger.info("📝 Filling date inputs...")
        start_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "start-date-filter-input")))
        end_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "end-date-filter-input")))
        start_input.clear()
        end_input.clear()
        start_input.send_keys(start_str)
        end_input.send_keys(end_str)

        logger.info(f"✅ Applying filter after {FILTER_TIME_TO_WAIT} seconds...")
        time.sleep(FILTER_TIME_TO_WAIT)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "apply-filter"))).click()
        logger.info("✅ Date filter applied successfully.")
    except Exception as e:
        logger.error(f"💥 Error in apply_date_filter: {e}")
        raise
