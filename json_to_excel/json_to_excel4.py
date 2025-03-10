import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> Dict:
    """JSON ob'ektni tekis qiladi, ichki massivlarni qayta ishlaydi"""
    flat_dict = {}

    # Asosiy maydonlar
    flat_dict['timestamp'] = (
        datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        if data.get('timestamp') else ''
    )
    flat_dict['title'] = (
        data.get('title', '').encode().decode('unicode_escape')
        if data.get('title') else ''
    )

    # Attachments qismi
    attachments = data.get('attachments', [])
    if attachments and 'data' in attachments[0]:
        for i, attachment in enumerate(attachments[0]['data'], 1):
            if 'external_context' in attachment and 'url' in attachment['external_context']:
                flat_dict[f'attachment_{i}_url'] = attachment['external_context']['url']

    # Data qismi
    for i, item in enumerate(data.get('data', []), 1):
        if 'update_timestamp' in item:
            flat_dict[f'data_{i}_update_timestamp'] = (
                datetime.fromtimestamp(item['update_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if item['update_timestamp'] else ''
            )

    return flat_dict


def process_json_file(input_file: str, output_file: str) -> None:
    """JSON fayldan ma'lumotlarni o'qib, XLSX ga yozadi"""
    records = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    records = [flatten_json(item) for item in data]
                else:
                    records.append(flatten_json(data))
            except json.JSONDecodeError:
                f.seek(0)
                records = [flatten_json(json.loads(line)) for line in f if line.strip()]

        if not records:
            print("Faylda ma'lumot topilmadi!")
            return

        # DataFrame yaratish
        df = pd.DataFrame(records)

        # Excel faylga yozish
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Event Data', index=False)

            # XlsxWriter ob'ektlarini olish
            worksheet = writer.sheets['Event Data']

            # Title uchun matn formati
            text_format = writer.book.add_format({
                'text_wrap': True,
                'valign': 'top'
            })

            # Ustun kengliklarini sozlash
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                width = 100 if col == 'title' else min(max_len, 50)
                worksheet.set_column(i, i, width, text_format if col == 'title' else None)

            # Title uchun qator balandligi
            worksheet.set_row(1, 100)

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'profile_posts_1.json'
    output_file = 'profile_posts_1.xlsx'
    process_json_file(input_file, output_file)