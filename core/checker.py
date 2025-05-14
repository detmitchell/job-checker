import hashlib
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from core.alerts import send_pushover_alert
from core.auth import login
from core.filters import apply_date_filter
from config import ALERT_CACHE_DURATION
from logger import logger

alerted_jobs = {}

def get_job_unique_id(job_row):
    """Generate a unique ID based on job attributes."""
    date = " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[2]/p')])
    time_str = " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[3]/p')])
    employee = " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[5]/p')])
    unique_str = f"{date}|{time_str}|{employee}"
    return hashlib.sha1(unique_str.encode('utf-8')).hexdigest()

def purge_old_alerts():
    """Remove cached job IDs that are older than ALERT_CACHE_DURATION."""
    now = datetime.now()
    to_remove = [job_id for job_id, ts in alerted_jobs.items() if now - ts > ALERT_CACHE_DURATION]
    for job_id in to_remove:
        del alerted_jobs[job_id]

def get_job_details(job_row):
    """Extract job details from a row element."""
    return {
        "date": " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[2]/p')]),
        "time": " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[3]/p')]),
        "duration": job_row.find_element(By.XPATH, './td[4]').text.strip(),
        "employee": " ".join([p.text.strip() for p in job_row.find_elements(By.XPATH, './td[5]/p')]),
        "classification": job_row.find_element(By.XPATH, './td[6]').text.strip(),
        "location": job_row.find_element(By.XPATH, './td[7]').text.strip()
    }

def check_for_new_jobs(driver):
    """Main job checker that logs in, filters jobs, and sends alerts."""
    try:
        login(driver)
        driver.get("https://ignite.sfe.powerschool.com/ui/#/substitute/jobs/available")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        apply_date_filter(driver)
        time.sleep(10)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "parent-table-desktop-available"))
        )

        job_rows = driver.find_elements(By.XPATH, "//table[@id='parent-table-desktop-available']//tbody//tr")
        for job_row in job_rows:
            job_id = get_job_unique_id(job_row)

            if job_id not in alerted_jobs:
                logger.info(f"🚨 New job found: {job_id}")
                job = get_job_details(job_row)
                message = (
                    f"New Job: {job['date'].split()[-1]}, "
                    f"{job['time'].replace(' AM', '-').replace(' PM', '')}, "
                    f"{job['employee']}, "
                    f"{job['classification']}, "
                    f"{job['location'].split(' - ')[-1]}"
                )
                try:
                    send_pushover_alert(message)
                    alerted_jobs[job_id] = datetime.now()
                    logger.info(f"✅ Alert sent and job cached: {job_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send alert for {job_id}: {e}")
            else:
                logger.info(f"ℹ️ Job already alerted: {job_id}")
    except Exception as e:
        logger.error(f"❌ Error checking for jobs: {e}")
        raise
