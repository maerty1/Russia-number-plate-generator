# Автоматическая генерация изображений автомобильных номеров

Этот проект предназначен для автоматической генерации изображений автомобильных номеров с аннотациями для обучения моделей компьютерного зрения, таких как YOLOv8. Проект включает в себя генерацию номеров с различными регионами, добавление случайных модификаторов к изображениям и создание аннотаций в формате YOLO.

## Особенности

- Генерация изображений автомобильных номеров с использованием SVG-шаблона.
- Поддержка различных регионов.
- Добавление случайных модификаторов к изображениям (размытие, изменение яркости, контраста, добавление грязи).
- Создание аннотаций в формате YOLO.
- Разделение данных на тренировочный, валидационный и тестовый наборы.

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/maerty1/Russia-number-plate-generator.git
    cd Russia-number-plate-generator
    ```

## Использование

1. Убедитесь, что у вас есть шрифт `RoadNumbers2.0.ttf` и SVG-шаблон `License_plate_in_Russia.svg` в корневой директории проекта.

2. Запустите скрипт для генерации изображений номеров:
    ```sh
    python app.py
    ```

3. Сгенерированные изображения и аннотации будут сохранены в директории `generated_plates_multiple_regions`.

## Параметры

- `FONT_PATH`: Путь к шрифту для отображения символов на номере.
- `SVG_PATH`: Путь к SVG-шаблону номера.
- `OUTPUT_DIR`: Директория для сохранения сгенерированных изображений и аннотаций.
- `PLATE_SIZE`: Размеры номера (ширина, высота).
- `FONT_SIZE`: Размер шрифта.
- `LEFT_OFFSET`: Отступ от левого края.
- `ELEMENT_OFFSET`: Отступ между элементами.
- `REGION_OFFSET`: Отступ для кода региона от остальных элементов.
- `LETTERS`: Список допустимых букв для номера.
- `DIGITS`: Список допустимых цифр для номера.
- `REGIONS`: Список регионов.
- `LETTER1_WIDTH`, `LETTER2_WIDTH`, `LETTER3_WIDTH`, `REGION_WIDTH`: Ширина для каждого элемента номера.
- `CLASS_MAPPING`: Соответствие символов и их классов для аннотаций.
- `MODIFIERS_PARAMS`: Параметры для случайных модификаторов изображений.

## Примеры

### Пример сгенерированного номера

![Пример номера](generated_plates_multiple_regions/train/images/A123BC123.png)

### Пример аннотации

10 0.05 0.5 0.1 1.0
1 0.15 0.5 0.1 1.0
2 0.25 0.5 0.1 1.0
3 0.35 0.5 0.1 1.0
15 0.45 0.5 0.1 1.0
11 0.55 0.5 0.1 1.0
12 0.65 0.5 0.1 1.0
1 0.75 0.5 0.1 1.0
5 0.85 0.5 0.1 1.0
2 0.95 0.5 0.1 1.0
