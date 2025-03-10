import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> Dict:
    """JSON ob'ektni tekis qiladi, Unicode belgilarni dekod qiladi"""
    flat_dict = {
        'fbid': data.get('fbid', ''),
        'timestamp': (
            datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            if data.get('timestamp') else ''
        )
    }

    for item in data.get('label_values', []):
        label = item['label']
        if 'value' in item:
            # Unicode belgilarni dekod qilish
            value = item['value'].encode().decode('unicode_escape')
            flat_dict[label] = value
        elif 'timestamp_value' in item:
            ts = item['timestamp_value']
            flat_dict[label] = (
                datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                if ts else ''
            )
        elif 'vec' in item:
            flat_dict[label] = '; '.join(
                str(v.get('value', '')).encode().decode('unicode_escape')
                for v in item['vec'] if v.get('value')
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
            df.to_excel(writer, sheet_name='Post Data', index=False)

            # XlsxWriter ob'ektlarini olish
            worksheet = writer.sheets['Post Data']

            # Matn uchun format
            text_format = writer.book.add_format({
                'text_wrap': True,  # Avtomatik qatorga bo'lish
                'valign': 'top'  # Yuqoridan tekislash
            })

            # Ustun kengliklarini sozlash
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                # Text ustuni uchun max kenglik 100, boshqalar uchun 50
                width = 100 if col == 'Text' else min(max_len, 50)
                worksheet.set_column(i, i, width, text_format if col == 'Text' else None)

            # Text ustuni uchun balandlikni sozlash
            worksheet.set_row(1, 200)  # 2-qator (1-indeks) uchun balandlik

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'edits_you_made_to_posts.json'
    output_file = 'edits_you_made_to_posts.xlsx'
    process_json_file(input_file, output_file)