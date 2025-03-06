import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List

# Load credentials and URLs
try:
    with open(r'C:\Users\user\PycharmProjects\data_scrip\linkedin\credentials_and_urls.json') as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    print("Error: credentials_and_urls.json file not found")
    exit(1)

# Setup Chrome driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Error initializing Chrome driver: {e}")
    exit(1)


def wait_for_correct_current_url(desired_url: str, timeout: int = 10) -> bool:
    try:
        WebDriverWait(driver, timeout).until(lambda driver: driver.current_url == desired_url)
        return True
    except:
        return False


# Login to LinkedIn
def linkedin_login():
    try:
        url = 'https://www.linkedin.com/login'
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        username = data["login_credentials"]["username"]
        password = data["login_credentials"]["password"]

        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        desired_url = 'https://www.linkedin.com/feed/'
        if not wait_for_correct_current_url(desired_url):
            raise Exception("Login failed or page didn't load correctly")
    except Exception as e:
        print(f"Login error: {e}")
        driver.quit()
        exit(1)


def scrape_profile(profile_url: str) -> Dict:
    profile_data = {'Name': '', 'Company': '', 'Location': '', 'Experience': [], 'Education': []}

    try:
        driver.get(profile_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mt2"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract basic info
        intro = soup.find('div', {'class': 'mt2 relative'})
        if intro:
            profile_data['Name'] = intro.find('h1').text.strip() if intro.find('h1') else ''
            company = soup.find('div', class_='text-body-medium')
            profile_data['Company'] = company.text.strip() if company else ''
            location = intro.find('span', {'class': 'text-body-small'})
            profile_data['Location'] = location.text.strip() if location else ''

        # Extract Experience
        exp_section = soup.find('section', {'class': lambda x: x and 'experience' in x.lower()})
        if exp_section:
            experiences = exp_section.find_all('li', {'class': 'artdeco-list__item'})
            for exp in experiences:
                exp_data = {}
                title = exp.find('span', {'class': 't-bold'})
                exp_data['Job Title'] = title.text.strip() if title else ''
                spans = exp.find_all('span', class_='t-14')
                exp_data['Company'] = spans[0].text.strip() if spans else ''
                exp_data['Date'] = spans[1].text.strip() if len(spans) > 1 else ''
                profile_data['Experience'].append(exp_data)

        # Extract Education
        edu_section = soup.find('section', {'class': lambda x: x and 'education' in x.lower()})
        if edu_section:
            educations = edu_section.find_all('li', {'class': 'artdeco-list__item'})
            for edu in educations:
                edu_data = {}
                school = edu.find('span', {'class': 't-bold'})
                edu_data['School Name'] = school.text.strip() if school else ''
                degree = edu.find('span', {'class': 't-14'})
                edu_data['Degree Name'] = degree.text.strip() if degree else ''
                field = edu.find('span', {'class': 'pv-entity__comma-item'})
                edu_data['Field of Study'] = field.text.strip() if field else ''
                dates = edu.find('span', {'class': 'pv-entity__dates'})
                edu_data['Dates Attended'] = dates.text.strip() if dates else ''
                profile_data['Education'].append(edu_data)

        return profile_data

    except Exception as e:
        print(f"Error scraping {profile_url}: {e}")
        return profile_data


def main():
    linkedin_login()
    profiles_data = []

    for profile_url in data["profile_urls"]:
        profile_data = scrape_profile(profile_url)
        profiles_data.append(profile_data)

        # Print scraped data
        print(f"\nScraped Profile Data:")
        print(f"Name: {profile_data['Name']}")
        print(f"Company: {profile_data['Company']}")
        print(f"Location: {profile_data['Location']}")
        print("Experience:")
        for exp in profile_data['Experience']:
            print(f" - Job Title: {exp['Job Title']}, Company: {exp['Company']}, Date: {exp['Date']}")
        print("Education:")
        for edu in profile_data['Education']:
            print(f" - School Name: {edu['School Name']}, Degree Name: {edu['Degree Name']}, "
                  f"Field of Study: {edu['Field of Study']}, Dates Attended: {edu['Dates Attended']}")

    driver.quit()

    # Convert to DataFrame and save
    profiles_df = pd.DataFrame(profiles_data)
    profiles_df['Experience'] = profiles_df['Experience'].apply(
        lambda x: '\n'.join([f"{exp['Job Title']} at {exp['Company']}, {exp['Date']}" for exp in x]) if x else ''
    )
    profiles_df['Education'] = profiles_df['Education'].apply(
        lambda x: '\n'.join(
            [f"{edu['School Name']}, {edu['Degree Name']}, {edu['Field of Study']}, {edu['Dates Attended']}"
             for edu in x]) if x else ''
    )

    try:
        profiles_df.to_csv('linkedin_profiles.csv', index=False, encoding='utf-8')
        print("\nLinkedIn profile data has been successfully saved to linkedin_profiles.csv.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


if __name__ == "__main__":
    main()