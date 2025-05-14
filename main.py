import sys
import time
from filelock import FileLock, Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from core.checker import check_for_new_jobs
from config import CHROME_HEADLESS
from logger import logger

LOCK_PATH = "script.lock"

def main_loop():
    while True:
        logger.info("🔁 Checking for jobs...")

        options = Options()
        if CHROME_HEADLESS:
            options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        try:
            check_for_new_jobs(driver)
        finally:
            driver.quit()
            logger.info("🧹 Browser closed.")

        logger.info("⏳ Waiting 1 minute...\n")
        time.sleep(60)

if __name__ == "__main__":
    lock = FileLock(LOCK_PATH)
    try:
        lock.acquire(timeout=1)
        main_loop()
    except KeyboardInterrupt:
        logger.warning("🛑 Stopped by user.")
    except Timeout:
        logger.warning("⚠️ Another instance is already running. Exiting.")
        sys.exit(1)
