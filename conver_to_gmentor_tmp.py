import os
from pathlib import Path
from datetime import datetime
import re
import html

excluded = {'.git', 'README.md', 'README', 'conver_to_gmentor_tmp.py', 'out.xml'}
creation_date = "01.03.2026 13:11"
header_postfix = "petr"

def parse_inline(text: str) -> str:
    """Парсинг inline-разметки Markdown в нужные теги."""

    # Экранируем HTML
    text = html.escape(text)

    # Ссылки вида [[target|name]] или [[target]] (до экранирования не нужно, т.к. | и [] не экранируются)
    # Сначала ссылки с именем: [[target|name]]
    text = re.sub(
        r'\[\[([^|\]]+)\|([^\]]+)\]\]',
        r'<a href="#board99999999">\2</a>',
        text
    )
    # Затем ссылки без имени: [[target]]
    text = re.sub(
        r'\[\[([^\]]+)\]\]',
        r'<a href="#board99999999">\1</a>',
        text
    )

    # Ссылки Markdown [name](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2">\1</a>',
        text
    )

    # Жирный **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # Курсив *text*
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)

    # Подчёркнутый __text__
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)

    # Зачёркнутый ~~text~~
    text = re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', text)

    return text


def parse_markdown_to_story(markdown: str) -> str:
    lines = markdown.split("\n")
    output = ['<story-text><div>']

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Пустая строка
        if not line:
            output.append("<div><br></div>")
            i += 1
            continue

        # Заголовки
        if line.startswith("### "):
            output.append(f"<h3>{parse_inline(line[4:])}</h3>")
            i += 1
        elif line.startswith("## "):
            output.append(f"<h2>{parse_inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("# "):
            output.append(f"<h1>{parse_inline(line[2:])}</h1>")
            i += 1

        # Ненумерованный список
        elif re.match(r"^[-*] ", line):
            output.append("<div><ul>")
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                item = re.sub(r"^[-*] ", "", lines[i].strip())
                output.append(f"<li>{parse_inline(item)}</li>")
                i += 1
            output.append("</ul></div>")

        # Нумерованный список
        elif re.match(r"^\d+\. ", line):
            output.append("<div><ol>")
            while i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                item = re.sub(r"^\d+\. ", "", lines[i].strip())
                output.append(f"<li>{parse_inline(item)}</li>")
                i += 1
            output.append("</ol></div>")

        # Таблица (pipe table)
        # Проверяем, что это действительно таблица, а не ссылка [[...|...]]
        elif "|" in line and "[[" not in line:
            table_lines = []
            while i < len(lines) and "|" in lines[i] and "[[" not in lines[i]:
                table_lines.append(lines[i])
                i += 1

            # Проверяем, что это хотя бы 3 строки (заголовок, разделитель, данные)
            if len(table_lines) >= 3 and all(c in table_lines[1] for c in "|-"):
                headers = [h.strip() for h in table_lines[0].split("|") if h.strip()]
                rows = [
                    [c.strip() for c in row.split("|") if c.strip()]
                    for row in table_lines[2:]
                ]

                output.append("<table><tbody><tr>")
                for h in headers:
                    output.append(
                        f'<th style="width:300px;"><td-editable>{parse_inline(h)}</td-editable></th>'
                    )
                output.append("</tr>")

                for row in rows:
                    output.append("<tr>")
                    for cell in row:
                        output.append(
                            f"<td><td-editable>{parse_inline(cell)}</td-editable></td>"
                        )
                    output.append("</tr>")

                output.append("</tbody></table>")
            else:
                # Это не таблица, обрабатываем как обычный текст
                output.append(f"<div>{parse_inline(line)}</div>")
                i += 1
        elif "|" in line and "[[" in line:
            # Строка содержит | но также и [[, это скорее всего ссылка, а не таблица
            output.append(f"<div>{parse_inline(line)}</div>")
            i += 1

        # Обычный текст
        else:
            output.append(f"<div>{parse_inline(line)}</div>")
            i += 1

    output.append("</div></story-text>")
    return "\n".join(output)


def remove_extention_from_name(original_name: str) -> str:
    return Path(original_name).stem


def scan_directory_xml(base_path: str, indent: int = 0, counters: dict = None) -> tuple[str, dict, dict]:
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
    

    links_tmp = {

    }
    for entry in entries:
        # Пропускаем исключённые элементы
        if entry in excluded:
            continue
        full_path = os.path.join(base_path, entry)
       
        is_dir = os.path.isdir(full_path)
        if not full_path.endswith('.md') and not is_dir:
            print(full_path)
            continue
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
            result.append(f'{indent_str}<gm-folder style="zoom: 1;" id=board"{unique_id}"> <name icon="fa fa-fw fa-folder">{original_name}</name>')
            # Рекурсивный вызов для директорий
            sub_result, counters, links = scan_directory_xml(full_path, indent + 1, counters)
            links_tmp = links_tmp | links
            if sub_result:
                result.append(sub_result)
            # Закрывающий тэг директории
            result.append(f'{indent_str}</gm-folder>')
        else:
            links_tmp[full_path.split('\\')[-1].split('.')[0]] = unique_id
            text = '<story-text><div>ПУСТО</div></story-text>'
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                text = parse_markdown_to_story(text)
            except Exception as e:
                print(f'[WARNING] {full_path} accuse error: "{e}"')
            result.append(f'{indent_str}<gm-story id="{unique_id}" > <name icon="fa fa-fw fa-file-text-o">{original_name}</name>  {text} </gm-story>')
    
    return '\n'.join(result), counters, links_tmp


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir_name = os.path.basename(script_dir)
    
    header = f"<gm-root>\n    <created_date>{creation_date}</created_date>\n    <modified_date>{datetime.now().strftime("%d.%m.%Y %H:%M")}</modified_date>\n    <name>{parent_dir_name}_{header_postfix}</name><portrait></portrait>\n"
    footer = "</gm-root>"
    # Сканируем директорию
    lines, _, links = scan_directory_xml(script_dir)
    print(links)
    
    # Собираем итоговый текст
    output_text = header + '\n' + lines
    
    # Записываем в txt файл
    output_file = os.path.join(script_dir, 'out.xml')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"Структура записана в файл: {output_file}")


if __name__ == '__main__':
    main()
