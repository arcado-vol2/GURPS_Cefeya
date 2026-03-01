import os
from pathlib import Path

excluded = {'.git', 'README.md', 'README'}
header_postfix = 'petr'

def remove_extention_from_name(original_name: str) -> str:
    return Path(original_name).stem


def scan_directory(base_path: str, indent_level: int = 0, counters: dict = None) -> tuple[list[str], dict]:
    result = []
    if counters is None:
        counters = {'dirs': 0, 'files': 0}
    
    

    try:
        entries = sorted(os.listdir(base_path))
    except PermissionError:
        return result, counters
    
    for entry in entries:
        # Пропускаем исключённые элементы
        if entry in excluded:
            continue
        full_path = os.path.join(base_path, entry)
        is_dir = os.path.isdir(full_path)
        
        # Формируем префикс из плюсов
        prefix = '+' * indent_level
        
        # Формируем тэг
        tag = 'dirs' if is_dir else 'files'
        
        # Инкрементируем счётчик и генерируем ID
        counters[tag] += 1
        unique_id = f"{tag}{counters[tag]:07d}"
        
        # Формируем оригинальное имя (без расширения для файлов)
        original_name = remove_extention_from_name(entry)
        
        # Формируем строку
        line = f"{prefix}{unique_id}_{original_name}"
        result.append(line)
        
        # Рекурсивный вызов для директорий
        if is_dir:
            sub_result, counters = scan_directory(full_path, indent_level + 1, counters)
            result.extend(sub_result)
    
    return result, counters


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir_name = os.path.basename(script_dir)
    
    header = f"# {parent_dir_name}_{header_postfix}"
    
    # Сканируем директорию
    lines, _ = scan_directory(script_dir)
    print(lines)


    # Собираем итоговый текст
    output_text = header + '\n' + '\n'.join(lines)
    
    # Записываем в txt файл
    output_file = os.path.join(script_dir, 'directory_structure.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"Структура записана в файл: {output_file}")


if __name__ == '__main__':
    main()
