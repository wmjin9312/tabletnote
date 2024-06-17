import pandas as pd

# 첫 번째 엑셀 파일 읽기
excel1_path = r'C:\Users\InE_MJ\Desktop\test\output.xlsx'
df1 = pd.read_excel(excel1_path)

# 두 번째 엑셀 파일 읽기
excel2_path = r'C:\Users\InE_MJ\Desktop\test\Category_definition.xlsx'
df2 = pd.read_excel(excel2_path)

# 결과를 저장할 열 추가
df1['category_type'] = ''
df1['keyword_count'] = 0  # 키워드 개수 저장할 열
df1['keywords_included'] = ''  # 포함된 키워드 목록 저장할 열

# 첫 번째 엑셀 파일을 순회하며 매칭 및 검사
for index1, row1 in df1.iterrows():
    ocr_textfile_path = row1['ocr_textfile_path']
    exam_class = row1['exam_class']
    subject = row1['subject']

    # 키워드 매칭을 위한 변수 초기화
    keyword_matching_count = {}
    included_keywords = set()  # 포함된 키워드 저장할 집합

    # txt 파일 읽기
    with open(ocr_textfile_path, 'r', encoding='utf-8') as txt_file:
        txt_content = txt_file.read()

    # 두 번째 엑셀 파일을 순회하며 매칭 확인
    for _, row2 in df2.iterrows():
        if exam_class == row2['exam_class'] and subject == row2['subject']:
            keyword_list = row2['keyword'].split(',')  # 키워드 수정
            for keyword in keyword_list:
                if keyword.strip() in txt_content:
                    included_keywords.add(keyword.strip())
                    keyword_matching_count[row2['category_type']] = keyword_matching_count.get(row2['category_type'], 0) + 1

    # 가장 많은 키워드가 매칭된 소분류 찾기
    if keyword_matching_count:
        max_matching_category = max(keyword_matching_count, key=keyword_matching_count.get)
        df1.at[index1, 'category_type'] = max_matching_category

    # 키워드 개수 및 목록 저장
    df1.at[index1, 'keyword_count'] = len(included_keywords)
    df1.at[index1, 'keywords_included'] = ', '.join(included_keywords)

# 결과 저장
result_excel_path = r'C:\Users\InE_MJ\Desktop\test\결과_엑셀_파일.xlsx'
df1.to_excel(result_excel_path, index=False)
print(f"결과가 {result_excel_path} 파일에 저장되었습니다.")

result_csv_path = r'C:\Users\InE_MJ\Desktop\test\결과_CSV_파일.csv'
df1.to_csv(result_csv_path, index=False, encoding='utf-8', sep=';')
print(f"결과가 {result_csv_path} 파일에 저장되었습니다.")