import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Rasmlarni saqlash uchun papka yaratamiz
save_path = "instagram_images"
os.makedirs(save_path, exist_ok=True)

# Chrome driver sozlash
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Brauzerni ko‘rsatmaslik uchun
options.add_argument("--disable-blink-features=AutomationControlled")

# Driverni ishga tushiramiz
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Instagram profiliga kirish
username = "digital_uz_"  # Do‘stingiz username-ni shu joyga yozing
profile_url = f"https://www.instagram.com/{username}/"
driver.get(profile_url)
time.sleep(5)

# Sahifani scroll qilish uchun funksiya
def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Sahifani oxirigacha siljitamiz
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Yangi kontent yuklanishi uchun kutamiz
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Agar yangi kontent yuklanmasa, to‘xtaymiz
            break
        last_height = new_height

# Sahifani scroll qilib, barcha postlarni yuklash
print("⏳ Sahifani scroll qilish boshlandi...")
scroll_to_bottom()
print("✅ Scroll qilish tugadi!")

# Postlar linklarini olish
post_links = []
posts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")

for post in posts:
    link = post.get_attribute("href")
    if link not in post_links:  # Takrorlanmas linklarni qo‘shish
        post_links.append(link)

print(f"✅ Topilgan postlar: {len(post_links)} ta")

# Rasm URL'larini yig'ish
image_urls = []

# Har bir postni ochib, rasm va kommentlarni olish
for idx, post in enumerate(post_links):  # Barcha postlarni qayta ishlash
    driver.get(post)
    time.sleep(3)

    try:
        # Post rasmini olish
        image = driver.find_element(By.CSS_SELECTOR, "img[style*='object-fit']")
        img_url = image.get_attribute("src")
        print(f"📸 {idx+1}-Rasm URL: {img_url}")

        # URL'ni listga qo'shish
        image_urls.append(img_url)

        # Kommentlarni olish (agar kerak bo‘lsa)
        comments = driver.find_elements(By.CSS_SELECTOR, "ul.XQXOT > ul > div > li")
        for comment in comments:
            try:
                username = comment.find_element(By.CSS_SELECTOR, "h3").text
                text = comment.find_element(By.CSS_SELECTOR, "span").text
                print(f"💬 {username}: {text}")
            except:
                continue
    except Exception as e:
        print(f"❌ {idx+1}-Postda xatolik: {e}")

# Selenium'ni yopish
driver.quit()

# 🔽 Rasmlarni yuklab olish va saqlash 🔽
for idx, img_url in enumerate(image_urls):
    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        # Fayl nomini yaratamiz (image_1.jpg, image_2.jpg, ...)
        file_name = os.path.join(save_path, f"image_{idx+1}.jpg")

        # Faylni saqlash
        with open(file_name, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"✅ Saqlandi: {file_name}")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

print("🎉 Barcha rasmlar saqlandi!")