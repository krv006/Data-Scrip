import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> List[Dict]:
    """JSON ob'ektni tekis qiladi, har bir video uchun alohida qator qaytaradi"""
    records = []

    for video in data.get('videos_v2', []):
        flat_dict = {
            'uri': video.get('uri', ''),
            'creation_timestamp': (
                datetime.fromtimestamp(video['creation_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if video.get('creation_timestamp') else ''
            ),
            'title': (
                video.get('title', '').encode().decode('unicode_escape')
                if video.get('title') else ''
            ),
            'description': (
                video.get('description', '').encode().decode('unicode_escape')
                if video.get('description') else ''
            )
        }

        # Media metadata qismi
        if 'media_metadata' in video and 'video_metadata' in video['media_metadata']:
            for exif in video['media_metadata']['video_metadata'].get('exif_data', []):
                flat_dict['upload_ip'] = exif.get('upload_ip', '')
                flat_dict['upload_timestamp'] = (
                    datetime.fromtimestamp(exif['upload_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    if exif.get('upload_timestamp') else ''
                )

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
            df.to_excel(writer, sheet_name='Videos Data', index=False)

            # XlsxWriter ob'ektlarini olish
            worksheet = writer.sheets['Videos Data']

            # Matnli ustunlar uchun format
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
                width = 100 if col in ['uri', 'description'] else min(max_len, 50)
                worksheet.set_column(i, i, width, text_format if col == 'description' else None)

            # Description uchun qator balandligi
            worksheet.set_row(1, 200)

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'videos.json'
    output_file = 'videos.xlsx'
    process_json_file(input_file, output_file)