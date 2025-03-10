import pandas as pd

# Define the data
data = {
    "name": [
        "Uzbekistan Offshore Outsourcing Conference'ga qo‘shiling",
        "Raqamli kelajak sari birinchi qadamni qo‘ying! Jonli efirga qo‘shiling!",
        "\"Bir million o'zbek dasturchilari\" loyihasi bo'yicha onlayn muloqot"
    ],
    "start_timestamp": [
        1740546000,
        1740045600,
        1735119000
    ],
    "end_timestamp": [0, 0, 0],
    "description": [
        "Sizni O‘zbekistoni global IT markazi sifatida kashf qilish imkoniyatini taqdim etuvchi Offshore Outsourcing Conference'ga taklif qilamiz!\n\nNega qatnashishingiz kerak?\n- O‘zbekiston hukumati yetakchilaridan biznes maqsadlaringizni qo‘llab-quvvatlash yo‘llarini bilib oling.\n- Strategik hamkorliklarni yo‘lga qo‘yib, qimmatli bilimlar orttiring.\n- HR ekspertlari bilan uchrashib, O‘zbekistonda mavjud malakali kadrlar haqida ma’lumotga ega bo‘ling.\n- 12 oylik bepul ofis maydoni va HR xarajatlarining qoplab berilishi kabi \"Zero Risk\" dasturi bilan tanishing.\n- Moliyaviy, yuridik, buxgalteriya va mehnat munosabatlariga bag‘ishlangan amaliy seminarlarda ishtirok eting.\n- Keyingi avlod IT mutaxassislarini tarbiyalayotgan yetakchi IT universitetlariga tashrif buyuring.\n- Mamlakatning yorqin madaniyati va quyoshli jozibasini o‘zida aks ettirgan sayohatlarda ishtirok eting.",
        "IT sohasida o‘qiyapsizmi? Yoki yangi imkoniyatlar izlayapsizmi?\nUnda 20-fevral soat 15:00 da bo‘lib o‘tadigan onlayn ochiq muloqot aynan Siz uchun!\n\nMuloqotda nimalar muhokama qilinadi?\n📹 IT sohasida o‘qish va rivojlanish yo‘llari;\n📹 Qizlar uchun ITga kirish va qo‘llab-quvvatlash dasturlari;\n📹 Yosh dasturchilar uchun yirik loyihalar:\n       ✅ (https://uzbekcoders.uz/) “Bir million o‘zbek dasturchi” (https://uzbekcoders.uz/) – dasturlashni bepul o‘rganish imkoniyati\n       ✅ ICPC Uzbekistan (https://www.icpc.uz/) – eng kuchli talabalar olimpiadasi\n       ✅ “President Tech Awards” (https://t.me/PresidentTechAward) – eng iqtidorli IT yoshlariga mukofotlar\n       ✅ Mirzo Ulug‘bek vorislari (https://vorislar.uz/) – ta’lim va ilmiy loyihalarni qo‘llab-quvvatlash\n       ✅  “JOB& EDU FEST” (https://t.me/mitcuz/16503) – ish topish va o‘qish uchun eng yaxshi platforma\n       ✅ “MAAB open source” – ochiq kod va innovatsiyalar maydoni\n       ✅ “UzGeeks Meetup” (https://www.uzgeeks.uz/) – IT jamoasi bilan tanishing va networking qiling\n\n📉 Ekspertlardan bevosita maslahat olish va o‘z savollaringizni berish imkoniyatini qo‘ldan boy bermang!",
        "Muloqot 2024-yil, 25-dekabr kuni, soat 14:30 da onlayn tarzda tashkil etiladi.\n\n✅📈 Xabaringiz bor, “Bir million dasturchi” loyihasining navbatdagi mavsumiga start berilgan edi. (https://t.me/digitaledu_uz/803)\n📈 Muloqot davomida, Siz:\n✅ IT sertifikatlarning foydali tomonlari;\n✅ Loyiha doirasidagi rag'batlantirish mexanizmlari;\n✅ O'quvchilarni loyihaga samarali jalb qilish;\n✅ Uzbekcoders.uz platformasidan oson va qulay foydalanish;\n✅ Bepul va pulli kurslar bo'yicha batafsil ma'lumotga ega bo'lasiz.\n\n📈Muloqotda loyiha mutaxassislariga o'zingizni qiziqtirgan savollar bilan murojaat qilishingiz mumkin.\n\n📉Eslatib o'tamiz, davlatimiz rahbari tomonidan loyihaning yangi bosqichi faol ishtirokchilari uchun ko'plab sovrinlar joriy etilgan."
    ],
    "create_timestamp": [
        1740493437,
        1739960717,
        1735033256
    ]
}

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Save to Excel
file_path = 'event_responses.xlsx'
df.to_excel(file_path, index=False)

