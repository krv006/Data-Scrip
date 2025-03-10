import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


def flatten_json(data: Dict) -> Dict:
    """JSON ob'ektni tekis qiladi, ichki tuzilmalarni qayta ishlaydi"""
    flat_dict = {}

    # Trash_v2 ichidagi har bir element uchun
    for item in data.get('trash_v2', []):
        flat_dict['timestamp'] = (
            datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            if item.get('timestamp') else ''
        )
        flat_dict['title'] = (
            item.get('title', '').encode().decode('unicode_escape')
            if item.get('title') else ''
        )

        # Attachments qismi
        for i, attachment in enumerate(item.get('attachments', []), 1):
            for j, att_data in enumerate(attachment.get('data', []), 1):
                if 'media' in att_data:
                    media = att_data['media']
                    flat_dict[f'media_uri'] = media.get('uri', '')
                    flat_dict[f'media_creation_timestamp'] = (
                        datetime.fromtimestamp(media['creation_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                        if media.get('creation_timestamp') else ''
                    )
                    flat_dict[f'media_title'] = (
                        media.get('title', '').encode().decode('unicode_escape')
                    )
                    flat_dict[f'media_description'] = (
                        media.get('description', '').encode().decode('unicode_escape')
                    )

                    # Media metadata
                    if 'media_metadata' in media and 'video_metadata' in media['media_metadata']:
                        for k, exif in enumerate(media['media_metadata']['video_metadata'].get('exif_data', []), 1):
                            flat_dict[f'exif_upload_ip'] = exif.get('upload_ip', '')
                            flat_dict[f'exif_upload_timestamp'] = (
                                datetime.fromtimestamp(exif['upload_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                                if exif.get('upload_timestamp') else ''
                            )

        # Data qismi (post)
        for i, data_item in enumerate(item.get('data', []), 1):
            if 'post' in data_item:
                flat_dict[f'post'] = (
                    data_item['post'].encode().decode('unicode_escape')
                )

    return flat_dict


def process_json_file(input_file: str, output_file: str) -> None:
    """JSON fayldan ma'lumotlarni o'qib, XLSX ga yozadi"""
    records = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records.append(flatten_json(data))

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
                width = 100 if col in ['title', 'media_description', 'post'] else min(max_len, 50)
                worksheet.set_column(i, i, width,
                                     text_format if col in ['title', 'media_description', 'post'] else None)

            # Qator balandligini sozlash
            worksheet.set_row(1, 200)

        print(f"Excel fayl '{output_file}' muvaffaqiyatli yaratildi!")
        print(f"Jami qayta ishlangan qatorlar: {len(records)}")

    except FileNotFoundError:
        print(f"Xatolik: '{input_file}' fayli topilmadi!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")


if __name__ == "__main__":
    input_file = 'trash.json'
    output_file = 'trash.xlsx'
    process_json_file(input_file, output_file)