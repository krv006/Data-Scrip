import os
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Load JSON file containing login credentials and profile URLs
json_path = os.path.join(os.path.dirname(__file__), 'credentials_and_urls.json')

if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
    raise FileNotFoundError(f"Error: '{json_path}' not found or is empty.")

with open(json_path, encoding='utf-8') as file:
    try:
        data = json.load(file)
        print("✅ JSON loaded successfully.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error: Invalid JSON format in '{json_path}': {e}")

# Setup Chrome WebDriver options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--headless")  # Run in headless mode for faster execution
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)


def wait_for_url_contains(substring, timeout=30):
    """Wait until the URL contains a specific substring, indicating successful navigation."""
    try:
        WebDriverWait(driver, timeout).until(EC.url_contains(substring))
        print(f"✅ Successfully navigated to {driver.current_url}")
        return True
    except TimeoutException:
        print(f"⚠️ Timeout: Page did not navigate to '{substring}' within {timeout} seconds.")
        return False


def login_to_linkedin(username, password):
    """Logs into LinkedIn using the provided credentials."""
    driver.get('https://www.linkedin.com/login')

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        if wait_for_url_contains('/feed'):
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed! Check credentials or CAPTCHA challenge.")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False


def scrape_profile(profile_url):
    """Scrapes data from a given LinkedIn profile URL."""
    profile_data = {'Name': '', 'Company': '', 'Location': '', 'Experience': [], 'Education': []}

    driver.get(profile_url)
    time.sleep(3)  # Small delay to ensure page loads completely

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except TimeoutException:
        print(f"⚠️ Timeout: Profile page '{profile_url}' did not load in time.")
        return profile_data

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract Name
    name_tag = soup.find('h1')
    profile_data['Name'] = name_tag.text.strip() if name_tag else 'N/A'

    # Extract Company (current workplace)
    company_tag = soup.find('div', class_='text-body-medium')
    profile_data['Company'] = company_tag.text.strip() if company_tag else 'N/A'

    # Extract Location
    location_tag = soup.find('span', {'class': 'text-body-small'})
    profile_data['Location'] = location_tag.text.strip() if location_tag else 'N/A'

    # Extract Experience
    experience_section = soup.find('section', {'id': 'experience'})
    if experience_section:
        for exp in experience_section.find_all('li', {'class': 'artdeco-list__item'}):
            exp_data = {
                'Job Title': exp.find('span').text.strip() if exp.find('span') else 'N/A',
                'Company': 'N/A',
                'Date': 'N/A'
            }
            company_exp_elements = exp.find_all('span', class_='t-14')
            if len(company_exp_elements) > 0:
                exp_data['Company'] = company_exp_elements[0].text.strip()
            if len(company_exp_elements) > 1:
                exp_data['Date'] = company_exp_elements[1].text.strip()
            profile_data['Experience'].append(exp_data)

    # Extract Education
    education_section = soup.find('section', {'id': 'education'})
    if education_section:
        for edu in education_section.find_all('li', {'class': 'artdeco-list__item'}):
            edu_data = {
                'School Name': edu.find('span', {'class': 't-bold'}).text.strip() if edu.find('span', {
                    'class': 't-bold'}) else 'N/A',
                'Degree Name': edu.find('span', {'class': 't-14'}).text.strip() if edu.find('span', {
                    'class': 't-14'}) else 'N/A',
                'Field of Study': 'N/A',
                'Dates Attended': 'N/A'
            }
            field_of_study_tag = edu.find('span', {'class': 'pv-entity__comma-item'})
            if field_of_study_tag:
                edu_data['Field of Study'] = field_of_study_tag.text.strip()
            dates = edu.find_all('span', class_='visually-hidden')
            if dates:
                edu_data['Dates Attended'] = dates[-1].text.strip()
            profile_data['Education'].append(edu_data)

    return profile_data


# Start the scraping process
if login_to_linkedin(data["login_credentials"]["username"], data["login_credentials"]["password"]):
    profiles_data = []

    for profile_url in data["profile_urls"]:
        print(f"\n🔍 Scraping profile: {profile_url}")
        profile_info = scrape_profile(profile_url)
        profiles_data.append(profile_info)
        print(f"✅ Profile '{profile_info['Name']}' scraped successfully.")

    # Close WebDriver
    driver.quit()

    # Convert data to Pandas DataFrame
    profiles_df = pd.DataFrame.from_records(profiles_data)

    # Format experience and education for CSV output
    profiles_df['Experience'] = profiles_df['Experience'].apply(
        lambda x: '\n'.join([f"{exp['Job Title']} at {exp['Company']}, {exp['Date']}" for exp in x]) if x else 'N/A'
    )
    profiles_df['Education'] = profiles_df['Education'].apply(
        lambda x: '\n'.join(
            [f"{edu['School Name']}, {edu['Degree Name']}, {edu['Field of Study']}, {edu['Dates Attended']}" for edu in
             x]) if x else 'N/A'
    )

    # Save to CSV
    profiles_df.to_csv('linkedin_profiles.csv', index=False, encoding='utf-8')
    print("\n✅ LinkedIn profile data successfully saved to 'linkedin_profiles.csv'.")
else:
    driver.quit()
    print("❌ Aborting scraping due to login failure.")
