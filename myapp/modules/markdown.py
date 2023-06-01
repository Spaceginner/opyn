HEADER_TEXT_SIZES = (3.5, 2.25, 1.75, 1.35, 1.25, 1.15)


def _get_text_size(header_size: int) -> int:
    if header_size < 1 or header_size > 6:
        raise ValueError("`header_size` has to be larger than 0 and less than 7")

    return HEADER_TEXT_SIZES[header_size-1]


def parse_text(s: str) -> str:
    modes: dict[str, bool] = {
        'italics': False,
        'bold': False,
        'underlined': False,
        'striked': False
    }
    buffer: str = ""
    skip: int = 0
    for i, char in enumerate(s):
        if skip > 0: skip -= 1; continue  # NOQA E702
        if s[i:i+2] == '**':
            if modes['bold']:
                modes['bold'] = False
                buffer += "</strong>"
            else:
                modes['bold'] = True
                buffer += "<strong>"
            skip = 1
        elif char == '*':
            if modes['italics']:
                modes['italics'] = False
                buffer += "</em>"
            else:
                modes['italics'] = True
                buffer += "<em>"
        elif s[i:i+2] == '__':
            if modes['underlined']:
                modes['underlined'] = False
                buffer += "</u>"
            else:
                modes['underlined'] = True
                buffer += "<u>"
            skip = 1
        elif char == '[':
            url_desc, url = "", ""
            j, k = 0, 0
            while s[i+1:][j] != ']':
                if j+1 == len(s[i:]) : break  # NOQA E701
                url_desc += s[i+1:][j]
                j += 1
            if s[i+j+2] == '(':
                while s[i+j+2:][k] != ')':
                    if k + 1 == len(s[i+j+2:]): break  # NOQA E701
                    url += s[i+j+3:][k]
                    k += 1
            buffer += f"<a href=\"{url[:-1]}\" target=\"_blank\" class=\"markdown-link\">{url_desc}</a>"
            skip = j+k+2

        else:
            buffer += char
    return buffer


def compile_md(raw_markdown: str) -> str:
    html = ""

    paragraph, previous_token_text = "", False
    md_lines = [line.strip() for line in raw_markdown.split('\n')]
    for i, md_line in enumerate(md_lines):
        if md_line.startswith('#'):  # header
            previous_token_text = False
            # i believe there should be a dedicated builtin method for this
            count = 0
            while md_line[count] == '#':
                count += 1

            if count > 6:  # ignore
                if i + 1 == len(md_lines) and md_line:
                    paragraph += f" {md_line}"
                if (md_lines[i] == '' or not previous_token_text or i + 1 == len(md_lines)) and paragraph.strip():
                    html += f"<p>{parse_text(paragraph.strip())}</p><br>\n"
                    paragraph = ""
                else:
                    paragraph += f" {md_line}"
                previous_token_text = True

            if md_line[count] == ' ':
                text_size = _get_text_size(count)
                html += f"<h{count} style=\"font-size: {text_size}rem\">" \
                        f"{md_line[count+1:].strip()}</h{count}>\n"
        elif md_line in ['---', '***']:
            previous_token_text = False
            html += "<hr>\n"
        else:  # normal text
            if i+1 == len(md_lines) and md_line:
                paragraph += f" {md_line}"
            if (md_lines[i] == '' or not previous_token_text or i+1 == len(md_lines)) and paragraph.strip():
                html += f"<p>{parse_text(paragraph.strip())}</p><br>\n"
                paragraph = ""
            else:
                paragraph += f" {md_line}"
            previous_token_text = True

    return html
