# needed for sorting
def _get_item_len(item):
    return len(item)

def _get_unique_items(items, allow_none: bool = True):
    unique_items = []

    for item in items:
        if not allow_none and item is None:
            continue

        if item not in unique_items:
            unique_items.append(item)

    return unique_items


# just a shorthand
def _join(s: list[str] | tuple[str]) -> str:
    return "".join(s)


def _contains_potential_tokens(raw_md: str, symbols: list[str] | tuple[str]) -> bool:
    for symbol in symbols:
        if symbol in raw_md:
            return True

    return False


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

        # this step will split up raw markdown
        # ie «text can be **bold** btw» will turn into
        # ["text can be ", "**", "bold", "**", " btw"]
        # it is just easier like this

        # the thing that will store splitted markdown
        raw_tokens: list[str] = []

        # get all unique symbols which are used for tokens
        # sorted from largest to smallest
        # we need this in order for it not to split up
        # a bigger token with a smaller one0
        unique_symbols = _get_unique_items(
            [token.raw['opening'] for token in self.tokens] + [token.raw['closing'] for token in self.tokens],
            allow_none=False
        )
        unique_symbols.sort(reverse=True, key=_get_item_len)

        # we will be checking at every point
        # if next symbols match any of the symbols
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

        # here we

        html, skip = "", 0


        for i in range(len(raw_tokens)):
            if skip: skip -= 1; continue  # NOQA E702

            match_found = False

            for token in self.tokens:
                # if there can't be any possible tokens left
                # just stop trying to match any tokens
                if i + 3 > len(raw_tokens):
                    break

                if raw_tokens[i] == token.raw['opening']:
                    j = 0
                    if token.raw['closing'] is not None:
                        j, invalid = 1, False
                        while raw_tokens[i+j] != token.raw['closing']:
                            j += 1
                            if i+j >= len(raw_tokens):
                                invalid = True; break  # NOQA E702
                        if invalid:
                            continue

                    token_content = _join(raw_tokens[i+1:i+j])

                    # if token contents themselves contain uncompiled markdown
                    # it is time for the oldest trick in the book: recursive function
                    # unfortunately this does mean it may give up if it will go too recursive
                    if _contains_potential_tokens(token_content, unique_symbols):
                        token_content = compile_md(token_content)

                    html += token.get_compiled(token_content)
                    skip = j
                    match_found = True
                    break

            if not match_found:
                html += raw_tokens[i]


        return html


def compile_md(raw_markdown: str) -> str:
    compiler = MarkdownCompiler()

    # headers
    compiler.add_token(Token('# ', '\r\n\r\n', '<h1 style=\"font-size: 3.5rem\">', '</h1><br>', True))
    compiler.add_token(Token('## ', '\r\n\r\n', '<h2 style=\"font-size: 2.25rem\">', '</h2><br>', True))
    compiler.add_token(Token('### ', '\r\n\r\n', '<h3 style=\"font-size: 1.75rem\">', '</h3><br>', True))
    compiler.add_token(Token('#### ', '\r\n\r\n', '<h4 style=\"font-size: 1.35rem\">', '</h4><br>', True))
    compiler.add_token(Token('##### ', '\r\n\r\n', '<h5 style=\"font-size: 1.25rem\">', '</h5><br>', True))
    compiler.add_token(Token('###### ', '\r\n\r\n', '<h6 style=\"font-size: 1.15rem\">', '</h6><br>', True))

    # text formatting
    compiler.add_token(Token('*', '*', '<em>', '</em>', True))
    compiler.add_token(Token('**', '**', '<strong>', '</strong>', True))
    compiler.add_token(Token('__', '__', '<u>', '</u>', True))
    compiler.add_token(Token('~~', '~~', '<s>', '</s>', True))

    # idk why but it fails to parse such thing by itself
    # so we have to register the thing separate manually
    compiler.add_token(Token('***', '***', '<strong><em>', '</em></strong>', True))

    # text align
    # we have to escape `<` and `>` as in HTML since the input is gonna be escaped, so we have to escape here too
    compiler.add_token(Token('-&gt;', '-&gt;', '<div style=\"text-align: right;\">', '</div>', True))
    compiler.add_token(Token('-&gt;', '&lt;-', '<div style=\"text-align: center;\">', '</div>', True))

    # horizontal rule
    compiler.add_token(Token('\r\n---\r\n', None, '<hr>', None, False))
    compiler.add_token(Token('\r\n***\r\n', None, '<hr>', None, False))

    # newline
    compiler.add_token(Token('\r\n\r\n', None, '<br>', None, False))
    compiler.add_token(Token('\r\n', None, ' ', None, False))

    return compiler.compile(raw_markdown + '\r\n\r\n')  # we have to add the token for break line manually as it gets stripped
