from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import credentials from auth_credential.py
from auth_credential import email, password


# WebDriver setup with enhanced error handling
def setup_driver():
    try:
        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {e}")
        traceback.print_exc()
        raise


# Login function with enhanced error handling
def perform_login(driver, email, password, wait, ec):
    try:
        # Open LinkedIn login page
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)  # Wait for page to load

        # Enter email
        username_button = wait.until(ec.presence_of_element_located((By.XPATH, "//input[@name='session_key']")))
        username_button.send_keys(email)

        # Enter password
        password_button = driver.find_element(By.XPATH, "//input[@name='session_password']")
        password_button.send_keys(password)

        # Click sign-in button
        sign_in_button = driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
        sign_in_button.click()
        time.sleep(3)  # Wait for login to complete

        logger.info("Login successful!")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        traceback.print_exc()
        raise


# Search and filter function with card clicking
def perform_search_and_filter(driver, wait, ec):
    try:
        # Navigate to the provided URL
        driver.get(
            "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22103644278%22%5D&keywords=front%20end%20developer&origin=FACETED_SEARCH&sid=KBx")
        logger.info("Navigated to search URL")
        time.sleep(2)  # Wait for page to load

        # Use the specific XPath for the first card
        card_xpath = "//*[@id]/div/ul/li[1]"  # Generalized to handle dynamic IDs
        first_card = wait.until(ec.element_to_be_clickable((By.XPATH, card_xpath)))

        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_card)
        time.sleep(1)

        # Click the card using JavaScript to ensure interaction
        driver.execute_script("arguments[0].click();", first_card)
        logger.info("Clicked first profile card")
        time.sleep(3)  # Wait for profile to load

        # Extract name from profile page
        try:
            name_element = wait.until(ec.presence_of_element_located((By.XPATH, "//span[@aria-hidden='true']")))
            name = name_element.text.strip() if name_element and name_element.text.strip() else "N/A"
            logger.info(f"Extracted name: {name}")
            return name
        except Exception as e:
            logger.error(f"Name extraction error: {e}")
            return "Name not found"

    except Exception as e:
        logger.error(f"Search and filter failed: {e}")
        traceback.print_exc()
        raise


# Main execution
if __name__ == "__main__":
    driver = None
    try:
        # Initialize driver
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)

        # Perform login
        perform_login(driver, email, password, wait, EC)

        # Perform search and extract profile
        extracted_name = perform_search_and_filter(driver, wait, EC)

        if extracted_name:
            print(f"Extracted Profile Name: {extracted_name}")
        else:
            print("No profile name extracted")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        # Ensure driver is closed
        if driver:
            input("Press Enter to close the browser...")
            driver.quit()