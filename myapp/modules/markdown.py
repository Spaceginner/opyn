def _get_item_len(item):
    return len(item)


class Token:
    def __init__(self, raw_opening: str, raw_closing: str | None, compiled_opening: str, compiled_closing: str | None, enclosed: bool):
        self.raw: dict[str, str] = {
            'opening': raw_opening,
            'closing': raw_closing
        }
        self.compiled: dict[str, str] = {
            'opening': compiled_opening,
            'closing': compiled_closing
        }
        self.enclosed = enclosed

    def get_compiled(self, s: str) -> str:
        return f"{self.compiled['opening']}" \
               f"{s if self.enclosed else ''}" \
               f"{self.compiled['closing'] if self.compiled['closing'] is not None else ''}"


class MarkdownCompiler:
    def __init__(self):
        self.tokens: list[Token] = []

    def add_token(self, token: Token):
        self.tokens.append(token)

    def compile(self, raw_md: str) -> str:
        # split.

        raw_tokens: list[str] = []

        unique_symbols = []
        for symbol in [token.raw['opening'] for token in self.tokens] + [token.raw['closing'] for token in self.tokens]:
            if symbol not in unique_symbols and symbol is not None:
                unique_symbols.append(symbol)

        unique_symbols.sort(reverse=True, key=_get_item_len)

        buffer, skip = "", 0
        for i in range(len(raw_md)):
            if skip: skip -= 1; continue  # NOQA E702

            match_found = False
            for unique_symbol in unique_symbols:
                if raw_md[i:i + len(unique_symbol)] == unique_symbol:
                    if buffer:
                        raw_tokens.append(buffer)
                        buffer = ""

                    raw_tokens.append(unique_symbol)
                    skip = len(unique_symbol) - 1
                    match_found = True
                    break
            if not match_found:
                buffer += raw_md[i]

        # match.

        html, skip = "", 0

        for i in range(len(raw_tokens)):
            if skip: skip -= 1; continue  # NOQA E702

            match_found = False

            for token in self.tokens:
                if i + 3 > len(raw_tokens):
                    break
                if raw_tokens[i] == token.raw['opening'] and \
                        (token.raw['closing'] is None or raw_tokens[i + 2] == token.raw['closing']):
                    html += token.get_compiled(raw_tokens[i + 1] if token.raw['closing'] is not None else raw_tokens[i])
                    skip = 2 if token.raw['closing'] is not None else 0
                    match_found = True
                    break
            if not match_found:
                html += raw_tokens[i]

        return html


def compile_md(raw_markdown: str) -> str:
    compiler = MarkdownCompiler()

    compiler.add_token(Token('# ', '\r\n\r\n', '<h1 style=\"font-size: 3.5rem\">', '</h1><br>', True))
    compiler.add_token(Token('## ', '\r\n\r\n', '<h2 style=\"font-size: 2.25rem\">', '</h2><br>', True))
    compiler.add_token(Token('### ', '\r\n\r\n', '<h3 style=\"font-size: 1.75rem\">', '</h3><br>', True))
    compiler.add_token(Token('#### ', '\r\n\r\n', '<h4 style=\"font-size: 1.35rem\">', '</h4><br>', True))
    compiler.add_token(Token('##### ', '\r\n\r\n', '<h5 style=\"font-size: 1.25rem\">', '</h5><br>', True))
    compiler.add_token(Token('###### ', '\r\n\r\n', '<h6 style=\"font-size: 1.15rem\">', '</h6><br>', True))

    compiler.add_token(Token('*', '*', '<em>', '</em>', True))
    compiler.add_token(Token('**', '**', '<strong>', '</strong>', True))
    compiler.add_token(Token('***', '***', '<strong><em>', '</em></strong>', True))
    compiler.add_token(Token('__', '__', '<u>', '</u>', True))

    compiler.add_token(Token('-&gt;', '-&gt;', '<div style=\"text-align: right;\">', '</div>', True))
    compiler.add_token(Token('-&gt;', '&lt;-', '<div style=\"text-align: center;\">', '</div>', True))

    compiler.add_token(Token('\r\n---\r\n', None, '<hr>', None, False))
    compiler.add_token(Token('\r\n***\r\n', None, '<hr>', None, False))

    compiler.add_token(Token('\r\n\r\n', None, '<br>', None, False))
    compiler.add_token(Token('\r\n', None, ' ', None, False))

    return compiler.compile(raw_markdown + '\r\n\r\n')
