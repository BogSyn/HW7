import sys
from pathlib import Path
import re
import shutil


JPEG_list = []
PNG_list = []
JPG_list = []
SVG_list = []

AVI_list = []
MP4_list = []
MOV_list = []
MKV_list = []

DOC_list = []
DOCX_list = []
TXT_list = []
PDF_list = []
XLSX_list = []
PPTX_list = []

MP3_list = []
OGG_list = []
WAV_list = []
AMR_list = []

ZIP_list = []
GZ_list = []
TAR_list = []

UNKNOWN_EXTENSIONS = []

REGISTER_EXTENSION = {
    'JPEG': JPEG_list,
    'PNG': PNG_list,
    'JPG': JPG_list,
    'SVG': SVG_list,
    'AVI': AVI_list,
    'MP4': MP4_list,
    'MOV': MOV_list,
    'MKV': MKV_list,
    'DOC': DOC_list,
    'DOCX': DOCX_list,
    'TXT': TXT_list,
    'PDF': PDF_list,
    'XLSX': XLSX_list,
    'PPTX': PPTX_list,
    'MP3': MP3_list,
    'OGG': OGG_list,
    'WAV': WAV_list,
    'AMR': AMR_list,
    'ZIP': ZIP_list,
    'GZ': GZ_list,
    'TAR': TAR_list,
}

FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()


# Витягуємо розширення, зрізаємо "." та переводимо у верхній регістр.


def get_extension(name: str) -> str:
    return Path(name).suffix[1:].upper()


# Робота з папками.


def scan(folder: Path):
    for item in folder.iterdir():                 # Ітеруємось по директорії.
        if item.is_dir():
            # Визначаємо папки, які пропускаємо
            if item.name not in ('images', 'documents', 'audio', 'video', 'archives', 'unknown_extension'):
                # Добавляємо в список всі шляхи до папок, крім вийнятків.
                FOLDERS.append(item)
                scan(item)                        # Рекурсія
            continue

        extension = get_extension(item.name)
        full_name = folder / item.name            # Повний шлях до файлу.
        # Добавляємо до списку шлях файлу, якщо немає розширеня.
        if not extension:
            UNKNOWN_EXTENSIONS.append(full_name)
        else:
            try:
                # Наповнюємо список словника файлами (повний шлях)
                take_from_dict = REGISTER_EXTENSION[extension]
                take_from_dict.append(full_name)
                # Добавляємо розширення (верзній регістр) до сету
                EXTENSIONS.add(extension)
            except KeyError:
                # Добавляємо до сету розширення, якщо невідоме.
                UNKNOWN.add(extension)
                # Добавляємо до списку шлях файлу, якщо невідоме розширеня.
                UNKNOWN_EXTENSIONS.append(full_name)


# Нормалізація файлів


UA_SYMBOLS = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLITERATION = ("a", "b", "v", "h", "g", "d", "e", "ie", "zh", "z", "y", "i", "yi", "i", "k", "l", "m", "n", "o", "p", "r", "s",
                   "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "yu", "ya")

TRANS_MAP = dict()

# Створюємо словник транслітерації.
for cyrillic, latin in zip(UA_SYMBOLS, TRANSLITERATION):
    TRANS_MAP[ord(cyrillic)] = latin
    TRANS_MAP[ord(cyrillic.upper())] = latin.upper()


def normalize(name: str) -> str:
    # Замінюємо будь-який символ крім цифри, букви та крапки на "_",  + робимо транслітерацію букв.
    translate_name = re.sub(r'[^\w\.]', '_', name.translate(TRANS_MAP))
    return translate_name


# Функція роботи з файлами.
# Створює цільовий каталог (якщо він не існує).
# Переносить нормалізований файл до відповідної папки.


def handle_files(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    file_name.replace(target_folder / normalize(file_name.name))

# Функція роботи з архівами.
# Створює цільовий каталог (якщо він не існує)
# Створює новий каталог для файлів, які були розпаковані з архіву.
# Ім'я цього каталогу базується на імені архіву,
# видаливши розширення файлу (.zip, .tar, тощо) і нормалізувавши його.


def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / \
        normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:  # Розпаковує архівний файл
        shutil.unpack_archive(str(file_name.absolute()),
                              str(folder_for_file.absolute()))
    except shutil.ReadError:  # Видаляє створений каталог і припиняє виконання функції
        folder_for_file.rmdir()
        return
    file_name.unlink()  # Видаляє архівний файл.


def main(folder: Path):
    scan(folder)
    # Обробляє відомі розширення
    for file in JPEG_list:
        handle_files(file, folder / 'images' / 'JPEG')
    for file in PNG_list:
        handle_files(file, folder / 'images' / 'PNG')
    for file in JPG_list:
        handle_files(file, folder / 'images' / 'JPG')
    for file in SVG_list:
        handle_files(file, folder / 'images' / 'SVG')
    for file in AVI_list:
        handle_files(file, folder / 'video' / 'AVI')
    for file in MP4_list:
        handle_files(file, folder / 'video' / 'MP4')
    for file in MOV_list:
        handle_files(file, folder / 'video' / 'MOV')
    for file in MKV_list:
        handle_files(file, folder / 'video' / 'MKV')
    for file in DOC_list:
        handle_files(file, folder / 'documents' / 'DOC')
    for file in DOCX_list:
        handle_files(file, folder / 'documents' / 'DOCX')
    for file in TXT_list:
        handle_files(file, folder / 'documents' / 'TXT')
    for file in PDF_list:
        handle_files(file, folder / 'documents' / 'PDF')
    for file in XLSX_list:
        handle_files(file, folder / 'documents' / 'XLSX')
    for file in PPTX_list:
        handle_files(file, folder / 'documents' / 'PPTX')
    for file in MP3_list:
        handle_files(file, folder / 'audio' / 'MP3')
    for file in OGG_list:
        handle_files(file, folder / 'audio' / 'OGG')
    for file in WAV_list:
        handle_files(file, folder / 'audio' / 'WAV')
    for file in AMR_list:
        handle_files(file, folder / 'audio' / 'AMR')
    # Обробляє невідомі розширення
    for file in UNKNOWN_EXTENSIONS:
        handle_files(file, folder / 'unknown_extension')
    # Обробляє відомі розширення архівів
    for file in ZIP_list:
        handle_archive(file, folder / 'archives')
    for file in GZ_list:
        handle_archive(file, folder / 'archives')
    for file in TAR_list:
        handle_archive(file, folder / 'archives')

    # Видаляє кожен елемент зі списку зворотньому порядку.
    for folder in FOLDERS[::-1]:
        try:
            folder.rmdir()
        except OSError:
            print(f'Error during remove folder {folder}')
    
    print(f'EXTENSIONS: {list(EXTENSIONS)}')
    print(f'UNKNOWN_EXTENSIONS: {list(UNKNOWN)}')


def clean_go():
    if sys.argv[1]:
        folder_process = Path(sys.argv[1])
        main(folder_process.resolve())

