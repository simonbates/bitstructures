class MarkdownLine:
    def __init__(self, line_of_text):
        self.text = line_of_text

    def is_blank(self):
        return (len(self.text) == 0) or self.text.isspace()

    def is_indented(self):
        return self.text.startswith('    ')

    def is_codeblock_line(self):
        return self.is_indented() or self.is_blank()

    def get_text_without_indentation(self):
        if self.is_indented():
            return self.text[4:]
        else:
            return self.text

def is_codeblock_header_field(line):
    if line.is_codeblock_line() and get_field_name(line):
        return True
    else:
        return False

def get_field_name(header_line):
    name_value = header_line.get_text_without_indentation()
    index = name_value.find(':')
    if index != -1:
        return name_value[0:index].strip()
    else:
        return None

def get_field_value(header_line):
    name_value = header_line.get_text_without_indentation()
    index = name_value.find(':')
    if index != -1:
        return name_value[index+1:].strip()
    else:
        return None

class MarkdownLineTokeniser:
    def __init__(self, text):
        self._lines = iter(text.splitlines(True))
        self.current_line = None
        self._at_end = False

    def is_at_end(self):
        return self._at_end

    def read_next(self):
        try:
            self.current_line = MarkdownLine(self._lines.next())
        except StopIteration:
            self._at_end = True
            self.current_line = None

class Section:
    def __init__(self):
        self.lines = list()

    def get_text(self):
        return ''.join(line.text for line in self.lines)

    def append(self, line):
        self.lines.append(line)

class Codeblock(Section):
    def __init__(self):
        Section.__init__(self)
        self.content_type = None

    def is_codeblock(self):
        return True

    def get_code(self):
        return ''.join(line.get_text_without_indentation() for line in self.lines)

class NonCodeblock(Section):
    def is_codeblock(self):
        return False

class MarkdownCodeblocksParser:
    def get_codeblock(self, text, n):
        if n < 1:
            return None
        count = 0
        lines = MarkdownLineTokeniser(text)
        lines.read_next()
        while not lines.is_at_end():
            if lines.current_line.is_indented():
                codeblock = self._get_codeblock(lines)
                count += 1
                if count == n:
                    return codeblock
            lines.read_next()
        return None

    def parse(self, text):
        sections = list()
        lines = MarkdownLineTokeniser(text)
        lines.read_next()
        while not lines.is_at_end():
            if lines.current_line.is_indented():
                sections.append(self._get_codeblock(lines))
            else:
                sections.append(self._get_non_codeblock(lines))
        return sections

    def _get_codeblock(self, lines):
        codeblock = Codeblock()
        if is_codeblock_header_field(lines.current_line):
            if get_field_name(lines.current_line) == 'Content-Type':
                codeblock.content_type = get_field_value(lines.current_line)
            lines.read_next()
        while (not lines.is_at_end()) and lines.current_line.is_codeblock_line():
            codeblock.append(lines.current_line)
            lines.read_next()
        return codeblock

    def _get_non_codeblock(self, lines):
        section = NonCodeblock()
        while (not lines.is_at_end()) and (not lines.current_line.is_indented()):
            section.append(lines.current_line)
            lines.read_next()
        return section
