import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> List[Dict]:
    """JSON ob'ektni tekis qiladi, har bir foto uchun alohida qator qaytaradi"""
    records = []

    for photo in data.get('other_photos_v2', []):
        flat_dict = {
            'uri': photo.get('uri', ''),
            'creation_timestamp': (
                datetime.fromtimestamp(photo['creation_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if photo.get('creation_timestamp') else ''
            )
        }

        # Media metadata qismi
        if 'media_metadata' in photo and 'photo_metadata' in photo['media_metadata']:
            for exif in photo['media_metadata']['photo_metadata'].get('exif_data', []):
                flat_dict['upload_ip'] = exif.get('upload_ip', '')

        records.append(flat_dict)

    return records


def process_json_file(input_file: str, output_file: str) -> None:
    """JSON fayldan ma'lumotlarni o'qib, XLSX ga yozadi"""
    records = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records.extend(flatten_json(data))

        if not records:
            print("Faylda ma'lumot topilmadi!")
            return

        # DataFrame yaratish
        df = pd.DataFrame(records)

        # Excel faylga yozish
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Photos Data', index=False)

            # XlsxWriter ob'ektlarini olish
            worksheet = writer.sheets['Photos Data']

            # Ustun kengliklarini sozlash
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                width = 100 if col == 'uri' else min(max_len, 50)
                worksheet.set_column(i, i, width)

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'uncategorized_photos.json'
    output_file = 'uncategorized_photos.xlsx'
    process_json_file(input_file, output_file)