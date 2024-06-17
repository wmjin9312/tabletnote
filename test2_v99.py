import requests
import os
from PIL import Image
import json
import uuid
import time
import base64
import pandas as pd

input_directory1 = r'C:\Users\InE_MJ\Desktop\test\result\Question_Q'

# 두 번째 이미지 디렉토리 경로
input_directory2 = r'C:\Users\InE_MJ\Desktop\test\result\Total'

# 첫 번째 결과 텍스트 저장 디렉토리
output_directory1 = r'C:\Users\InE_MJ\Desktop\test\result\ocr_files_Question_q'

# 두 번째 결과 텍스트 저장 디렉토리
output_directory2 = r'C:\Users\InE_MJ\Desktop\test\result\ocr_files_Total'

# 네이버 Clova OCR API 설정
client_secret = 'eEZOcE1TbUtwR0dzb0hkT01CaUtMa3JxREpjdG93VnE='
ocr_url = 'https://ruogt8u3o1.apigw.ntruss.com/custom/v1/27686/c47ecef621a8e4aaae4e3c405de6913b9c108e09fe2b20bc4c54bc91aa171266/general'

def extract_text_from_image_clova(image_path):
    headers = {
        'X-OCR-SECRET': client_secret,
        'Content-Type': 'application/json',
    }

    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        encoded_image_data = base64.b64encode(image_data).decode('utf-8')
        request_json = {
            'images': [
                {
                    'format': 'png',
                    'name': os.path.basename(image_path),
                    'language': 'ko',
                    'data': encoded_image_data
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000)),
        }

        response = requests.post(ocr_url, headers=headers, json=request_json)

    if response.status_code != 200:
        print(f"Error in OCR API call: {response.status_code}")
        print(response.text)  # 오류 응답 본문 출력
        return None

    result = response.json()

    extracted_texts = []
    for field in result['images'][0]['fields']:
        text = field['inferText']
        extracted_texts.append(text)

    return ' '.join(extracted_texts)

def save_extracted_text(image_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    extracted_text = extract_text_from_image_clova(image_path)

    if extracted_text is None:
        print(f"No text extracted from {image_path}")
        return

    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{base_filename}_ocr_files_Total.txt"
    output_path = os.path.join(output_directory, output_filename)

    with open(output_path, 'w', encoding='utf-8') as text_file:
        text_file.write(extracted_text)

    print(f"Extracted text saved to: {output_path}")



# 디렉토리 내 모든 이미지에 대해 작업 수행
for filename in os.listdir(input_directory1):
    if filename.endswith(".png"):  # 이미지 파일만 처리
        image_path = os.path.join(input_directory1, filename)
        save_extracted_text(image_path, output_directory1)

# 두 번째 디렉토리 내 모든 이미지에 대해 OCR 수행
for filename in os.listdir(input_directory2):
    if filename.endswith(".png"):  # 이미지 파일만 처리
        image_path = os.path.join(input_directory2, filename)
        save_extracted_text(image_path, output_directory2)


# 현재 디렉토리 경로를 가져옵니다.
current_dir = r'C:\Users\InE_MJ\Desktop\test'

# 폴더명 CSV 파일명, 엑셀 파일명 설정
folder_name = 'result'
csv_filename = 'output.csv'
excel_filename = 'output.xlsx'

# 폴더 경로와 CSV 파일 경로를 절대 경로로 변경합니다.
folder_path = os.path.join(current_dir, folder_name)
csv_path = os.path.join(current_dir, csv_filename)
excel_path = os.path.join(current_dir, excel_filename)

# 파일 목록을 저장할 데이터프레임을 생성합니다.
file_data = pd.DataFrame(columns=['File Name', 'File Content'])

# 폴더 내의 파일 목록 가져오기
file_names = os.listdir(folder_path)

# 변수 초기화
for file_name in file_names:
    globals()[file_name + '_list'] = []

for file_name in file_names:
    # 각 하위 폴더의 파일을 탐색하여 딕셔너리에 저장
    subfolder_path = os.path.join(folder_path, file_name)

    for root, _, files in os.walk(subfolder_path):
        for file in files:
            full_file_path = os.path.join(root, file)  # 전체 파일 경로 생성
            if file_name in file:
                globals()[file_name + '_list'].append(full_file_path)
            if "extracted_text" in file:
                globals()['extracted_text_files_list'].append(full_file_path)

df = pd.DataFrame()
df['total_img_path'] = Total_list
# df['answer_img_path'] = Answer_list
# df['question_q_img_path'] = Question_Q_list
df['ocr_textfile_path'] = ocr_files_Total_list

# 디렉토리 없으면 생성
os.makedirs(os.path.dirname(csv_path), exist_ok=True)

# CSV 파일 저장
df.to_csv(csv_path, index=False)

# CSV 파일을 읽어와 엑셀 파일로 저장
r_csv = pd.read_csv(csv_path)
r_csv.to_excel(excel_path, index=False)  # xlsx 파일로 변환