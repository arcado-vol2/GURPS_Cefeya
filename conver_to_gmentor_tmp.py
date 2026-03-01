import os
from pathlib import Path

excluded = {'.git', 'README.md', 'README'}


def remove_extention_from_name(original_name: str) -> str:
    return Path(original_name).stem


def scan_directory_xml(base_path: str, indent: int = 0, counters: dict = None) -> tuple[str, dict]:
    """Рекурсивно сканирует директорию и возвращает XML-подобную строку и счётчики."""
    result = []
    
    # Инициализируем счётчики при первом вызове
    if counters is None:
        counters = {'d': 0, 'f': 0}
    
    # Отступ для текущей строки
    indent_str = '    ' * indent
    
    try:
        entries = sorted(os.listdir(base_path))
    except PermissionError:
        return '', counters
    
    for entry in entries:
        # Пропускаем исключённые элементы
        if entry in excluded:
            continue
        full_path = os.path.join(base_path, entry)
        is_dir = os.path.isdir(full_path)
        
        # Инкрементируем счётчик и генерируем ID
        if is_dir:
            counters['d'] += 1
            unique_id = f"d{counters['d']:07d}"
            tag_name = 'dir'
        else:
            counters['f'] += 1
            unique_id = f"f{counters['f']:07d}"
            tag_name = 'file'
        
        # Формируем оригинальное имя (без расширения для файлов)
        original_name = remove_extention_from_name(entry)
        
        if is_dir:
            # Открывающий тэг директории
            result.append(f'{indent_str}<dir name="{original_name}" id="{unique_id}">')
            # Рекурсивный вызов для директорий
            sub_result, counters = scan_directory_xml(full_path, indent + 1, counters)
            if sub_result:
                result.append(sub_result)
            # Закрывающий тэг директории
            result.append(f'{indent_str}</dir>')
        else:
            # Файл с парными тэгами
            result.append(f'{indent_str}<file name="{original_name}" id="{unique_id}"></file>')
    
    return '\n'.join(result), counters


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir_name = os.path.basename(script_dir)
    
    header = f"# {parent_dir_name}"
    
    # Сканируем директорию
    lines, _ = scan_directory_xml(script_dir)
    
    # Собираем итоговый текст
    output_text = header + '\n' + lines
    
    # Записываем в txt файл
    output_file = os.path.join(script_dir, 'directory_structure.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"Структура записана в файл: {output_file}")


if __name__ == '__main__':
    main()
