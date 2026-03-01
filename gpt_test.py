import re
import html


def parse_inline(text: str) -> str:
    """Парсинг inline-разметки Markdown в нужные теги."""

    # Экранируем HTML
    text = html.escape(text)

    # Ссылки
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
        elif "|" in line:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1

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

        # Обычный текст
        else:
            output.append(f"<div>{parse_inline(line)}</div>")
            i += 1

    output.append("</div></story-text>")
    return "\n".join(output)



md = """
# Заголовок 1

Простой текст

## Заголовок 2

- пункт 1
- пункт 2

1. Пункт 1
2. Пункт 2

| Колонка 1 | Колонка 2 |
|-----------|-----------|
| Ячейка 1  | Ячейка 2  |

Текст с [ссылкой](#test) и **жирным** и *курсивом* и __подчёркнутым__ и ~~зачёркнутым~~
"""

print(parse_markdown_to_story(md))