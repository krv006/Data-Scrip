import csv
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import os
import signal
import sys


# Global variable to store freelancer data
freelancer_data = []

# Job categories to scrape
JOB_CATEGORIES = [
    "Tech freelancers", "Frontend Devs", "Backend Devs", "Full-stack Devs", "Web designers", "UI/UX",
    "Creative freelancers", "Social Media Managers", "Photographers", "Videographers", "Editors",
    "Animators", "Motion Graphics Artists", "Graphic Designers", "Music/Audio"
]


def signal_handler(sig, frame):
    """Handle Ctrl+C interrupt and save data before exiting."""
    print("\nCtrl+C detected! Saving data before exit...")
    if freelancer_data:
        save_to_csv(freelancer_data)
        save_to_json(freelancer_data)
        print("Data saved successfully.")
    else:
        print("No data to save.")
    if 'driver' in globals():
        driver.quit()  # Ensure driver is closed
    sys.exit(0)


def init_driver():
    """Initialize Chrome WebDriver with specific version."""
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        # Specify Chrome version 133 to match your installed browser
        driver = uc.Chrome(version_main=133, options=options)
        print("ChromeDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"Failed to initialize ChromeDriver: {e}")
        print("Ensure Chrome 133 is installed and matches the ChromeDriver version.")
        sys.exit(1)


def save_to_csv(data_list):
    """Save the scraped data to a CSV file with minimal quoting."""
    filename = "hubstaff_freelancer_data.csv"
    headers = ["Name", "Job Title", "Location", "Skills", "Hourly Rate", "Bio", "Profile URL"]

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows([[d['name'], d['job_title'], d['location'], d['skills'],
                           d['hourly_rate'], d['bio'], d['profile_url']] for d in data_list])
    print(f"Data saved to {filename}")


def save_to_json(data_list):
    """Save the scraped data to a JSON file."""
    filename = "hubstaff_freelancer_data.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump({"freelancers": data_list}, file, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")


def get_profile_details(driver, profile_url):
    """Extract detailed information from a freelancer's profile page."""
    try:
        print(f"Navigating to profile: {profile_url}")
        driver.get(profile_url)
        time.sleep(3)  # Allow page to render

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Scrape Bio
        bio = "N/A"
        try:
            bio_elem = soup.select_one("div.profile-bio")
            bio = bio_elem.text.strip().replace('\n', ' | ') if bio_elem else "N/A"
            print(f"Scraped Bio: {bio[:50]}..." if len(bio) > 50 else f"Scraped Bio: {bio}")
        except Exception as e:
            print(f"Error scraping Bio: {e}")

        # Scrape Hourly Rate
        hourly_rate = "N/A"
        try:
            rate_elem = soup.select_one("div.hourly-rate")
            hourly_rate = rate_elem.text.strip() if rate_elem else "N/A"
            print(f"Scraped Hourly Rate: {hourly_rate}")
        except Exception as e:
            print(f"Error scraping Hourly Rate: {e}")

        # Scrape Skills
        skills = []
        try:
            skill_elements = soup.select("div.skill-tag")
            skills = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
            print(f"Scraped Skills: {skills}")
        except Exception as e:
            print(f"Error scraping Skills: {e}")

        return {
            'bio': bio,
            'hourly_rate': hourly_rate,
            'skills': ', '.join(skills) if skills else "N/A"
        }

    except Exception as e:
        print(f"Error scraping profile {profile_url}: {e}")
        return {'bio': 'N/A', 'hourly_rate': 'N/A', 'skills': 'N/A'}


def scrape_hubstaff_freelancers():
    """Scrape data for freelancers from Hubstaff Talent."""
    global freelancer_data, driver
    driver = init_driver()

    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        for job_category in JOB_CATEGORIES:
            print(f"\nScraping freelancers for job category: {job_category}")

            page_num = 1
            while True:
                # Navigate to the search page for the job category
                search_url = f"https://talent.hubstaff.com//search//?loc=united-states&nbs=1&q=Music%2FAudio&page={page_num}"
                print(f"Opening search page {page_num}: {search_url}")
                driver.get(search_url)

                # Wait for freelancers to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.profile-card'))
                )

                # Parse page source with BeautifulSoup
                search_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Get all freelancer elements
                profile_cards = search_soup.select('div.profile-card')
                print(f"Found {len(profile_cards)} freelancers on page {page_num}")

                if not profile_cards:
                    print(f"No more freelancers found on page {page_num}. Moving to next category.")
                    break

                for card in profile_cards:
                    try:
                        # Extract basic data from search page
                        name = card.select_one('h4.profile-name').text.strip()
                        job_title = card.select_one('div.profile-title').text.strip()
                        location = card.select_one('div.profile-location').text.strip()
                        profile_url = card.select_one('a.profile-link')['href']

                        # Check if the freelancer is from the US
                        if "United States" not in location:
                            print(f"Skipping {name} (Location: {location})")
                            continue

                        print(f"\nProcessing freelancer: {name} ({job_title})")

                        # Get detailed profile information
                        profile_details = get_profile_details(driver, profile_url)

                        # Combine all data
                        freelancer = {
                            'name': name,
                            'job_title': job_title,
                            'location': location,
                            'skills': profile_details['skills'],
                            'hourly_rate': profile_details['hourly_rate'],
                            'bio': profile_details['bio'],
                            'profile_url': profile_url
                        }

                        freelancer_data.append(freelancer)
                        print(f"Completed scraping {name}")

                    except Exception as e:
                        print(f"Error processing freelancer: {e}")
                        continue

                # Move to next page
                page_num += 1

        # Save data
        if freelancer_data:
            save_to_csv(freelancer_data)
            save_to_json(freelancer_data)

            # Print summary
            print("\nFinal Results Summary:")
            print(f"Total freelancers scraped: {len(freelancer_data)}")
            for i, freelancer in enumerate(freelancer_data, 1):
                print(f"\n{i}. {freelancer['name']} ({freelancer['job_title']})")
                print(f"   Location: {freelancer['location']}")
                print(f"   Hourly Rate: {freelancer['hourly_rate']}")
                print(f"   Skills: {freelancer['skills']}")
        else:
            print("No freelancer data was collected.")

    except Exception as e:
        print(f"Unexpected error: {e}")
        if freelancer_data:  # Save on unexpected errors too
            save_to_csv(freelancer_data)
            save_to_json(freelancer_data)

    finally:
        try:
            driver.quit()
            print("Driver closed.")
        except Exception as e:
            print(f"Error closing driver: {e}")


if __name__ == "__main__":
    scrape_hubstaff_freelancers()
