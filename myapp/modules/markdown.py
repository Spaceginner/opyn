HEADER_TEXT_SIZES = (4.5, 3.25, 2.75, 2, 1.75, 1.5)


def _get_text_size(header_size: int) -> int:
    if header_size < 1 or header_size > 6:
        raise ValueError("`header_size` has to be larger than 0 and less than 7")

    return HEADER_TEXT_SIZES[header_size-1]


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
                if md_lines[i] == '' and paragraph.strip():
                    html += f"<p>{paragraph.strip()}</p><br>\n"
                    paragraph = ""
                elif i + 1 == len(md_lines) and md_line.strip():
                    html += f"<p>{md_line.strip()}</p><br>\n"
                else:
                    paragraph += f" {md_line}"

            if md_line[count] == ' ':
                text_size = _get_text_size(count)
                html += f"<h{count} style=\"font-size: {text_size}rem\">" \
                        f"{md_line[count+1:].strip()}</h{count}>\n"
        elif md_line in ['---', '***']:
            previous_token_text = False
            html += "<hr>\n"
        else:  # normal text
            if (md_lines[i] == '' or not previous_token_text) and paragraph.strip():
                html += f"<p>{paragraph.strip()}</p><br>\n"
                paragraph = ""
            elif i+1 == len(md_lines) and md_line.strip():
                html += f"<p>{md_line.strip()}</p><br>\n"
            else:
                paragraph += f" {md_line}"
            previous_token_text = True

    return html
