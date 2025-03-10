import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> Dict:
    """Bir JSON ob'ektni tekis qiladi"""
    flat_dict = {'fbid': data.get('fbid', '')}

    for item in data.get('label_values', []):
        label = item['label']
        if 'value' in item:
            flat_dict[label] = item['value']
        elif 'timestamp_value' in item:
            ts = item['timestamp_value']
            flat_dict[label] = (
                datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                if ts else ''
            )
    return flat_dict


def process_json_file(input_file: str, output_file: str) -> None:
    """JSON fayldan ma'lumotlarni o'qib, XLSX ga yozadi"""
    # Barcha qatorlarni saqlash uchun ro'yxat
    records = []

    # Faylni qator-qator o'qish (xotira tejash uchun)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # Agar faylda bitta katta JSON array bo'lsa
            try:
                data = json.load(f)
                if isinstance(data, list):
                    records = [flatten_json(item) for item in data]
                else:
                    records.append(flatten_json(data))
            # Agar faylda har bir qatorda alohida JSON bo'lsa
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
            df.to_excel(writer, sheet_name='Contact Sync Settings', index=False)

            # Ustun kengliklarini sozlash
            worksheet = writer.sheets['Contact Sync Settings']
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, min(max_len, 50))

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'contacts_sync_settings.json'
    output_file = 'contacts_sync_settings.xlsx'
    process_json_file(input_file, output_file)