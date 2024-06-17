from PIL import Image, ImageDraw
from ultralytics import YOLO
import json
import os

# 이미지가 있는 디렉토리 경로
input_directory = r'C:\Users\InE_MJ\Desktop\test\original'
output_directory = r'C:\Users\InE_MJ\Desktop\test\result'  # 결과 이미지 및 JSON 저장 디렉토리

image_files = [os.path.join(input_directory, filename) for filename in os.listdir(input_directory) if filename.endswith('.png')]

def load_image(image_path):
    return Image.open(image_path)

def get_image_width(image_path):
    with Image.open(image_path) as img:
        return img.width

def calculate_box_center(coordinates):
    x1, y1, x2, y2 = coordinates
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def sort_total_objects(objects, image_path):
    image_width = get_image_width(image_path)
    image_center_x = image_width / 2

    left_of_center = []
    right_of_center = []

    for obj in objects:
        center = calculate_box_center(obj["coordinates"])
        if center[0] < image_center_x:
            left_of_center.append(obj)
        else:
            right_of_center.append(obj)

    # 왼쪽 객체들을 y값이 작은 순으로 정렬
    left_of_center.sort(key=lambda x: calculate_box_center(x["coordinates"])[1])

    # 오른쪽 객체들을 y값이 작은 순으로 정렬
    right_of_center.sort(key=lambda x: calculate_box_center(x["coordinates"])[1])

    # 왼쪽 객체들을 먼저, 그 다음 오른쪽 객체들
    sorted_objects = left_of_center + right_of_center
    return sorted_objects

def crop_image(image, coordinates):
    cropped_image = image.crop(coordinates)
    # Add your resizing logic here if needed
    # Example: resized_image = cropped_image.resize((new_width, new_height))
    return cropped_image

def draw_boxes_on_downloaded_image(image_file, json_file):
    # 이미지 로드
    image = Image.open(image_file)

    # JSON 파일 로드
    with open(json_file, 'r') as file:
        detected_objects = json.load(file)

    # 이미지에 바운딩 박스 그리기
    draw = ImageDraw.Draw(image)
    for obj in detected_objects:
        box = obj['coordinates']
        draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="red", width=3)

    # 결과 이미지 저장 및 표시
    output_image_path = 'output_with_boxes_v2.jpg'
    image.save(output_image_path)
    return output_image_path

# 모델 로드
model = YOLO('C:\\Users\\InE_MJ\\Desktop\\tabletnotedb\\default.pt')

# 디렉토리 내 모든 이미지에 대해 작업 수행
for image_path in image_files:
    if image_path.endswith(".png"):  # 이미지 파일만 처리
        # 이미지에서 객체 감지
        results = model(image_path)

        # 결과 처리
        detected_objects = []
        for r in results:
            detection_classes = r.boxes.cls.tolist()
            bounding_box_pts_float = r.boxes.xyxy.tolist()

            bounding_box_pts_float_rounded = []
            for box in bounding_box_pts_float:
                bounding_box_pts_float_rounded.append([round(box[0], 2), round(box[1], 2), round(box[2], 2), round(box[3], 2)])

            # 각 객체의 정보를 JSON 형식으로 변환
            for cls, bbox in zip(detection_classes, bounding_box_pts_float_rounded):
                cls_int = int(cls)  # 클래스 인덱스를 정수로 변환
                detected_objects.append({
                    "label": model.names[cls_int],
                    "coordinates": bbox,
                    "confidence": r.boxes.conf[cls_int].item()
                })

        # 원본 이미지의 JSON 파일 경로 생성
        json_file_path = os.path.splitext(image_path)[0] + '_detected_objects.json'

        # JSON 파일로 저장
        with open(json_file_path, 'w') as file:
            json.dump(detected_objects, file, indent=4)

        # 라운드 박스 그리기
        draw_boxes_on_downloaded_image(image_path, json_file_path)

# detected_objects 로드
for image_path in image_files:
    if image_path.endswith(".png"):  # 이미지 파일만 처리
        json_file_path = os.path.splitext(image_path)[0] + '_detected_objects.json'
        with open(json_file_path, 'r') as file:
            detected_objects = json.load(file)

        # "Total" 레이블을 가진 객체들만 추출
        get_total_objects = [obj for obj in detected_objects if obj['label'] == 'Total']

        sorted_total_objects = sort_total_objects(get_total_objects, image_path)

        # Define the labels to consider
        labels_to_check = ["Answer", "Option_Picture", "Option_Table", "Option_Text", "Question", "Question_Q"]

        # Initialize a dictionary to store total objects and their children
        total_and_sub_objects = []

        # Iterate through sorted_total_objects
        for total_obj in sorted_total_objects:
            total_coordinates = total_obj["coordinates"]
            total_children = []

            # Iterate through data to find children
            for obj in detected_objects:
                label = obj["label"]
                coordinates = obj["coordinates"]
                confidence = obj["confidence"]
                x_center = (coordinates[0] + coordinates[2]) / 2
                y_center = (coordinates[1] + coordinates[3]) / 2

                if label in labels_to_check and total_coordinates[0] < x_center < total_coordinates[2] and total_coordinates[1] < y_center < total_coordinates[3]:
                    total_children.append({"label": label, "coordinates": coordinates, "confidence": confidence})

            total_obj["children"] = total_children
            total_and_sub_objects.append(total_obj)

        # Now total_objects contains Total objects with their children
        file_path = os.path.splitext(image_path)[0] + '_total_and_sub_objects.json'

        # Save the total_objects list to a JSON file
        with open(file_path, "w") as json_file:
            json.dump(total_and_sub_objects, json_file, indent=4)

def extract_coordinates_by_label(json_file_path, target_label):
    coordinates_list = []
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        for obj in data:
            if 'children' in obj:
                for child_obj in obj['children']:
                    if child_obj['label'] == target_label:
                        coordinates_list.append(child_obj['coordinates'])
    return coordinates_list

def save_images_for_labels(json_file_path, image_path, target_labels, output_directory):
    original_image = load_image(image_path)
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    # 레이블 디렉토리 생성
    os.makedirs(output_directory, exist_ok=True)

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for total_index, item in enumerate(data):
        if item['label'] == 'Total':
            # 'Total' 이미지 저장
            total_coordinates = item['coordinates']
            cropped_total = crop_image(original_image, total_coordinates)
            total_image_path = os.path.join(output_directory, "Total", f"{base_filename}_Total_{total_index + 1}.png")
            os.makedirs(os.path.dirname(total_image_path), exist_ok=True)
            cropped_total.save(total_image_path)

            # 'Total'의 자식 이미지들 저장
            for child_index, child in enumerate(item.get('children', [])):
                child_label = child['label']
                if child_label in target_labels:
                    if child_label == "Question":  # 'Question' 레이블은 건너뜀
                        continue

                    if child_label in ["Option_Picture", "Option_Table", "Option_Text"]:
                        child_label_directory = os.path.join(output_directory, "Option")
                        file_label = "Option"
                    else:
                        child_label_directory = os.path.join(output_directory, child_label)
                        file_label = child_label

                    child_image_name = f"{base_filename}_{file_label}_{total_index + 1}.png"
                    child_image_path = os.path.join(child_label_directory, child_image_name)

                    os.makedirs(child_label_directory, exist_ok=True)
                    cropped_child = crop_image(original_image, child['coordinates'])
                    cropped_child.save(child_image_path)

# Example usage:
target_labels = ["Answer", "Question_Q", "Option_Picture", "Option_Table", "Option_Text"]
for image_path in image_files:
    json_file_path = os.path.splitext(image_path)[0] + '_total_and_sub_objects.json'
    save_images_for_labels(json_file_path, image_path, target_labels, output_directory)
