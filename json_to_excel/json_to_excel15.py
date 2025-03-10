import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> Dict:
    """JSON ob'ektni tekis qiladi"""
    flat_dict = {
        'fbid': data.get('fbid', ''),
        'timestamp': (
            datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            if data.get('timestamp') else ''
        ),
        'title': (
            data.get('title', '').encode().decode('unicode_escape')
            if data.get('title') else ''
        )
    }

    # Label_values qismi
    for item in data.get('label_values', []):
        label = item['label']
        if 'value' in item:
            flat_dict[label] = (
                item['value'].encode().decode('unicode_escape')
                if item.get('value') else ''
            )
        elif 'timestamp_value' in item:
            ts = item['timestamp_value']
            flat_dict[label] = (
                datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                if ts > 0 else 'Not set'
            )
        elif 'dict' in item:
            for sub_item in item['dict']:
                flat_dict[f"{label}_{sub_item['label']}"] = sub_item['value']

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
                width = 100 if col in ['title', 'Event host'] else min(max_len, 50)
                worksheet.set_column(i, i, width, text_format if col in ['title', 'Event host'] else None)

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'events_you_hosted.json'
    output_file = 'events_you_hosted.xlsx'
    process_json_file(input_file, output_file)