import instaloader
import os
import time

# Rasmlarni saqlash uchun papka yaratamiz
save_path = "instagram_images"
os.makedirs(save_path, exist_ok=True)

# Instaloader ob'ektini yaratamiz
L = instaloader.Instaloader(
    download_pictures=True,
    download_videos=False,
    download_comments=False,
    save_metadata=False
)

# Profilni yuklash
username = "digital_uz_"  # Do‘stingizning username-ni shu yerga yozing
try:
    profile = instaloader.Profile.from_username(L.context, username)
    print(f"✅ Profil topildi: {profile.username}")
    print(f"Postlar soni: {profile.mediacount}")
    print(f"Obunachilar: {profile.followers}")
    print(f"Obunalar: {profile.followees}")
except Exception as e:
    print(f"❌ Profilni yuklashda xatolik: {e}")
    exit()

print("⏳ Postlarni yuklash boshlandi...")
image_count = 0

for post in profile.get_posts():
    try:
        # Postni yuklash
        L.download_post(post, target=save_path)
        image_count += 1
        print(f"✅ {image_count}-post yuklandi: {post.shortcode}")

        # Instagram bloklashdan saqlanish uchun uzoqroq pauza
        time.sleep(10)  # Har bir postdan keyin 10 soniya kutish
    except Exception as e:
        print(f"❌ {post.shortcode} postida xatolik: {e}")
        time.sleep(60)  # Xatolikdan keyin 1 daqiqa kutish
        continue

print(f"🎉 Yuklash tugadi! Jami {image_count} ta post saqlandi.")