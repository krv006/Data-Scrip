import instaloader
import os
import csv
import time

# Instaloader ob'ektini yaratamiz
L = instaloader.Instaloader()

# Sessiya fayli
session_file = "session_k.qakhramanovich"

# Instagram hisobiga kirish
my_username = "k.qakhramanovich"  # Sizning username’ingiz
my_password = "asdfghjkjhgfd"     # Sizning parolingizni shu yerga yozing

if os.path.exists(session_file):
    # Sessiyani fayldan yuklash
    try:
        L.load_session_from_file(my_username, session_file)
        print("✅ Sessiya fayldan yuklandi!")
    except Exception as e:
        print(f"❌ Sessiyani yuklashda xatolik: {e}")
        exit()
else:
    # Yangi sessiya yaratish
    try:
        L.login(my_username, my_password)
        L.save_session_to_file(session_file)
        print("✅ Instagram hisobiga kirildi va sessiya saqlandi!")
    except Exception as e:
        print(f"❌ Hisobga kirishda xatolik: {e}")
        exit()

# O‘z profilini yuklash
try:
    profile = instaloader.Profile.from_username(L.context, my_username)
    print(f"✅ Profil topildi: {profile.username}")
    print(f"Obunachilar soni: {profile.followers}")
    print(f"Maxfiy hisob: {profile.is_private}")
except Exception as e:
    print(f"❌ Profilni yuklashda xatolik: {e}")
    exit()

# CSV faylni yaratish
csv_file = f"{my_username}_followers.csv"
followers_list = []

# O‘z obunachilarini yuklash
print("⏳ Obunachilarni yuklash boshlandi...")
try:
    for follower in profile.get_followers():
        followers_list.append(follower.username)
        print(f"✅ Obunachi qo‘shildi: {follower.username}")
        time.sleep(10)  # Bloklashdan saqlanish uchun 10 soniya pauza
except Exception as e:
    print(f"❌ Obunachilarni yuklashda xatolik (batafsil): {repr(e)}")
    print(f"Xatolik turi: {type(e).__name__}")
    time.sleep(60)  # Xatolikdan keyin 1 daqiqa kutish

# CSV faylga yozish
try:
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Username"])
        for follower in followers_list:
            writer.writerow([follower])
    print(f"✅ Obunachilar {csv_file} fayliga saqlandi! Jami: {len(followers_list)} ta.")
except Exception as e:
    print(f"❌ CSV faylga yozishda xatolik: {e}")

print("🎉 Jarayon tugadi!")