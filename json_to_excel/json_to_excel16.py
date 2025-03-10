import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> List[Dict]:
    """JSON ob'ektni tekis qiladi, har bir event uchun alohida qator qaytaradi"""
    records = []

    for event in data.get('your_events_v2', []):
        flat_dict = {
            'name': (
                event.get('name', '').encode().decode('unicode_escape')
                if event.get('name') else ''
            ),
            'start_timestamp': (
                datetime.fromtimestamp(event['start_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if event.get('start_timestamp') > 0 else 'Not set'
            ),
            'end_timestamp': (
                datetime.fromtimestamp(event['end_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if event.get('end_timestamp') > 0 else 'Not set'
            ),
            'description': (
                event.get('description', '').encode().decode('unicode_escape')
                if event.get('description') else ''
            ),
            'create_timestamp': (
                datetime.fromtimestamp(event['create_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                if event.get('create_timestamp') > 0 else 'Not set'
            )
        }
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
            df.to_excel(writer, sheet_name='Events Data', index=False)

            # XlsxWriter ob'ektlarini olish
            worksheet = writer.sheets['Events Data']

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
                width = 100 if col in ['name', 'description'] else min(max_len, 50)
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
    input_file = 'events.json'
    output_file = 'events.xlsx'
    process_json_file(input_file, output_file)