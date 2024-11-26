import itertools
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cairosvg

# Параметры
FONT_PATH = "RoadNumbers2.0.ttf"  # Укажите путь к шрифту
SVG_PATH = "License_plate_in_Russia.svg"  # Укажите путь к SVG-файлу
OUTPUT_DIR = "generated_plates_multiple_regions"  # Папка для сохранения номеров
PLATE_SIZE = (520, 112)  # Размеры номера
FONT_SIZE = 135  # Размер шрифта
LEFT_OFFSET = 40  # Отступ от левого края
ELEMENT_OFFSET = -10  # Отступ между элементами
REGION_OFFSET = 40  # Отступ для кода региона от остальных элементов

# Русские буквы
LETTERS = ["A", "B", "C", "E", "H", "K", "M", "O", "P", "T", "X", "Y"]
DIGITS = "0123456789"
REGIONS = ["222", "777"]  # Список регионов

LETTER1_WIDTH = 58
LETTER2_WIDTH = 76
LETTER3_WIDTH = 58
REGION_WIDTH = 95  # Увеличенная ширина для кода региона

# Соответствие символов и их классов
CLASS_MAPPING = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'E': 13, 'H': 14, 'K': 15, 'M': 16, 'O': 17,
    'P': 18, 'T': 19, 'X': 20, 'Y': 21
}

# Параметры модификаторов
MODIFIERS_PARAMS = {
    'blur_radius': (2.0, 5.0),  # Диапазон радиуса размытия
    'brightness_factor': (0.5, 1.5),  # Диапазон изменения яркости
    'contrast_factor': (0.5, 1.5),  # Диапазон изменения контраста
    'dirt_count': (1, 5),  # Количество пятен грязи
    'dirt_radius': (5, 20)  # Радиус пятен грязи
}

def resize_text(draw, text, font, target_width):
    """Возвращает шрифт, масштабированный для заданной ширины текста."""
    while True:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if text_width <= target_width:
            break
        font_size = font.size - 1
        if font_size < 1:
            raise ValueError("Слишком малый размер шрифта.")
        font = ImageFont.truetype(font.path, font_size)
    return font

def draw_plate(number, font_path, svg_path, output_dir, left_offset, element_offset, region_offset):
    """Создает изображение номерного знака."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Преобразование SVG в изображение
    cairosvg.svg2png(url=svg_path, write_to=os.path.join(output_dir, 'temp_plate.png'), output_width=PLATE_SIZE[0], output_height=PLATE_SIZE[1])
    img = Image.open(os.path.join(output_dir, 'temp_plate.png'))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, FONT_SIZE)

    x_offset = left_offset
    y_position = 30

    elements = [
        (number[0], LETTER1_WIDTH),
        (number[1:4], 3 * LETTER1_WIDTH),
        (number[4], LETTER2_WIDTH),
        (number[5], LETTER3_WIDTH),
    ]

    annotations = []

    for text, target_width in elements:
        resized_font = resize_text(draw, text, font, target_width)
        text_bbox = draw.textbbox((0, 0), text, font=resized_font)
        text_width = text_bbox[2] - text_bbox[0]
        x_centered = x_offset + (target_width - text_width) // 2
        draw.text((x_centered, y_position), text, font=resized_font, fill="black")

        # Добавление аннотаций
        for char in text:
            char_bbox = draw.textbbox((x_centered, y_position), char, font=resized_font)
            char_width = char_bbox[2] - char_bbox[0]
            x_center = (x_centered + char_width / 2) / PLATE_SIZE[0]
            y_center = 0.5  # Центр по высоте платы
            width = char_width / PLATE_SIZE[0]
            height = 1.0  # Высота платы
            class_id = CLASS_MAPPING[char]
            annotations.append(f"{class_id} {x_center} {y_center} {width} {height}")
            x_centered += char_width

        # Добавление отступа между элементами
        x_offset += target_width + element_offset

    # Добавление кода региона справа от остальных элементов
    region_text = number[6:]
    region_width = REGION_WIDTH
    resized_font = resize_text(draw, region_text, font, region_width)
    text_bbox = draw.textbbox((0, 0), region_text, font=resized_font)
    text_width = text_bbox[2] - text_bbox[0]
    x_centered = PLATE_SIZE[0] - region_offset - text_width
    draw.text((x_centered, y_position), region_text, font=resized_font, fill="black")

    # Добавление аннотаций для кода региона
    for char in region_text:
        char_bbox = draw.textbbox((x_centered, y_position), char, font=resized_font)
        char_width = char_bbox[2] - char_bbox[0]
        x_center = (x_centered + char_width / 2) / PLATE_SIZE[0]
        y_center = 0.5  # Центр по высоте платы
        width = char_width / PLATE_SIZE[0]
        height = 1.0  # Высота платы
        class_id = CLASS_MAPPING[char]
        annotations.append(f"{class_id} {x_center} {y_center} {width} {height}")
        x_centered += char_width

    output_path = os.path.join(output_dir, f"{number}.png")
    img.save(output_path)

    # Удаление временного файла
    os.remove(os.path.join(output_dir, 'temp_plate.png'))

    return annotations, img

def create_annotation(number, annotations, output_dir):
    """Создает файл аннотаций для YOLOv8."""
    annotation_path = os.path.join(output_dir, f"{number}.txt")
    with open(annotation_path, 'w') as f:
        for annotation in annotations:
            f.write(annotation + '\n')

def generate_all_numbers(letters, digits, regions):
    """Генерирует все возможные номера для заданных регионов."""
    for region in regions:
        for letter1 in letters:
            for digit_combo in itertools.product(digits, repeat=3):
                for letter2 in letters:
                    for letter3 in letters:
                        yield f"{letter1}{''.join(digit_combo)}{letter2}{letter3}{region}"

def split_data(data, ratios):
    """Разделяет данные на тренировочный, валидационный и тестовый наборы."""
    train_size = int(len(data) * ratios[0])
    val_size = int(len(data) * ratios[1])
    test_size = len(data) - train_size - val_size

    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]

    return train_data, val_data, test_data

def add_modifiers(img, params):
    """Добавляет случайные модификаторы к изображению."""
    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(*params['blur_radius'])))
    if random.random() < 0.5:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(*params['brightness_factor']))
    if random.random() < 0.5:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(random.uniform(*params['contrast_factor']))
    if random.random() < 0.5:
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(*params['dirt_count'])):
            x = random.randint(0, PLATE_SIZE[0])
            y = random.randint(0, PLATE_SIZE[1])
            r = random.randint(*params['dirt_radius'])
            draw.ellipse((x - r, y - r, x + r, y + r), fill="black")
    return img

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_numbers = list(generate_all_numbers(LETTERS, DIGITS, REGIONS))

    # Лимит на количество номеров
    LIMIT = 20000
    all_numbers = all_numbers[:LIMIT]

    # Разделение данных
    train_numbers, val_numbers, test_numbers = split_data(all_numbers, [0.7, 0.2, 0.1])

    # Создание каталогов
    os.makedirs(os.path.join(OUTPUT_DIR, 'train/images'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'train/labels'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'valid/images'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'valid/labels'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'test/images'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'test/labels'), exist_ok=True)

    # Сохранение данных
    for idx, plate_number in enumerate(train_numbers):
        annotations, img = draw_plate(plate_number, FONT_PATH, SVG_PATH, os.path.join(OUTPUT_DIR, 'train/images'), LEFT_OFFSET, ELEMENT_OFFSET, REGION_OFFSET)
        img = add_modifiers(img, MODIFIERS_PARAMS)
        img.save(os.path.join(OUTPUT_DIR, 'train/images', f"{plate_number}.png"))
        create_annotation(plate_number, annotations, os.path.join(OUTPUT_DIR, 'train/labels'))
        if idx % 1000 == 0:  # Отображение прогресса
            print(f"Сохранено {idx} тренировочных номеров...")

    for idx, plate_number in enumerate(val_numbers):
        annotations, img = draw_plate(plate_number, FONT_PATH, SVG_PATH, os.path.join(OUTPUT_DIR, 'valid/images'), LEFT_OFFSET, ELEMENT_OFFSET, REGION_OFFSET)
        img = add_modifiers(img, MODIFIERS_PARAMS)
        img.save(os.path.join(OUTPUT_DIR, 'valid/images', f"{plate_number}.png"))
        create_annotation(plate_number, annotations, os.path.join(OUTPUT_DIR, 'valid/labels'))
        if idx % 1000 == 0:  # Отображение прогресса
            print(f"Сохранено {idx} валидационных номеров...")

    for idx, plate_number in enumerate(test_numbers):
        annotations, img = draw_plate(plate_number, FONT_PATH, SVG_PATH, os.path.join(OUTPUT_DIR, 'test/images'), LEFT_OFFSET, ELEMENT_OFFSET, REGION_OFFSET)
        img = add_modifiers(img, MODIFIERS_PARAMS)
        img.save(os.path.join(OUTPUT_DIR, 'test/images', f"{plate_number}.png"))
        create_annotation(plate_number, annotations, os.path.join(OUTPUT_DIR, 'test/labels'))
        if idx % 1000 == 0:  # Отображение прогресса
            print(f"Сохранено {idx} тестовых номеров...")

    # Создание файла data.yaml
    data_yaml = f"""train: train/images
val: valid/images
test: test/images

names:
  0: 0
  1: 1
  2: 2
  3: 3
  4: 4
  5: 5
  6: 6
  7: 7
  8: 8
  9: 9
  10: A
  11: B
  12: C
  13: E
  14: H
  15: K
  16: M
  17: O
  18: P
  19: T
  20: X
  21: Y
"""
    with open(os.path.join(OUTPUT_DIR, 'data.yaml'), 'w') as f:
        f.write(data_yaml)
