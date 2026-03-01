import os
import hashlib
from pathlib import Path


def generate_unique_id(path: str, is_dir: bool) -> str:
    """Генерирует уникальный ID из 8 цифр на основе пути."""
    hash_obj = hashlib.md5(path.encode())
    hash_hex = hash_obj.hexdigest()
    # Берём первые 7 цифр из хеша
    digits = ''.join(c for c in hash_hex if c.isdigit())[:7]
    # Первая цифра: 0 для директорий, 1 для файлов
    first_digit = '0' if is_dir else '1'
    return first_digit + digits


def format_name(original_name: str) -> str:
    """Убирает расширение из имени файла."""
    return Path(original_name).stem


def scan_directory(base_path: str, indent_level: int = 0) -> list[str]:
    """Рекурсивно сканирует директорию и возвращает список строк."""
    result = []
    
    # Исключаемые элементы
    excluded = {'.git', 'README.md', 'README'}
    
    try:
        entries = sorted(os.listdir(base_path))
    except PermissionError:
        return result
    
    for entry in entries:
        # Пропускаем исключённые элементы
        if entry in excluded:
            continue
        full_path = os.path.join(base_path, entry)
        is_dir = os.path.isdir(full_path)
        
        # Формируем префикс из плюсов
        prefix = '+' * indent_level
        
        # Генерируем ID
        unique_id = generate_unique_id(full_path, is_dir)
        
        # Формируем тэг
        tag = 'd' if is_dir else 'f'
        
        # Формируем оригинальное имя (без расширения для файлов)
        original_name = format_name(entry)
        
        # Формируем строку
        line = f"{prefix}{tag}_{unique_id}_{original_name}"
        result.append(line)
        
        # Рекурсивный вызов для директорий
        if is_dir:
            result.extend(scan_directory(full_path, indent_level + 1))
    
    return result


def main():
    # Получаем директорию, из которой вызван файл
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Получаем имя родительской директории
    parent_dir_name = os.path.basename(script_dir)
    
    # Формируем заголовок
    header = f"# {parent_dir_name}"
    
    # Сканируем директорию
    lines = scan_directory(script_dir)
    
    # Собираем итоговый текст
    output_text = header + '\n' + '\n'.join(lines)
    
    # Записываем в txt файл
    output_file = os.path.join(script_dir, 'directory_structure.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"Структура записана в файл: {output_file}")


if __name__ == '__main__':
    main()
