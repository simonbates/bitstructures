from bitstructures.substructure.codeblocks import MarkdownLine, MarkdownCodeblocksParser, is_codeblock_header_field, get_field_name, get_field_value
import unittest

class MarkdownLineTest(unittest.TestCase):
    def setUp(self):
        self.empty = MarkdownLine('')
        self.foo_bar = MarkdownLine('    foo:bar')
        self.foo_bar_spaces = MarkdownLine('    foo : bar')
        self.foo_bar_newline = MarkdownLine('    foo:bar\n')

    def test_is_blank(self):
        self.assert_(self.empty.is_blank())
        self.assert_(MarkdownLine(' ').is_blank())
        self.assert_(MarkdownLine('\t').is_blank())
        self.assert_(MarkdownLine('\n').is_blank())
        self.assert_(MarkdownLine(' \n').is_blank())
        self.assert_(MarkdownLine('\t\n').is_blank())

    def test_is_indented(self):
        self.assert_(MarkdownLine('    code').is_indented())
        self.assert_(MarkdownLine('     code').is_indented())

    def test_codeblock_header_field(self):
        self.assert_(not is_codeblock_header_field(self.empty))
        self.assert_(not is_codeblock_header_field(MarkdownLine('foo')))
        self.assert_(not is_codeblock_header_field(MarkdownLine('foo:bar')))
        self.assert_(not is_codeblock_header_field(MarkdownLine('    foo')))
        self.assert_(not is_codeblock_header_field(MarkdownLine('    :')))
        self.assert_(not is_codeblock_header_field(MarkdownLine('    :foo')))
        self.assert_(is_codeblock_header_field(self.foo_bar))
        self.assertEqual('foo', get_field_name(self.foo_bar))
        self.assertEqual('bar', get_field_value(self.foo_bar))
        self.assert_(is_codeblock_header_field(self.foo_bar_spaces))
        self.assertEqual('foo', get_field_name(self.foo_bar_spaces))
        self.assertEqual('bar', get_field_value(self.foo_bar_spaces))
        self.assert_(is_codeblock_header_field(self.foo_bar_newline))
        self.assertEqual('foo', get_field_name(self.foo_bar_newline))
        self.assertEqual('bar', get_field_value(self.foo_bar_newline))

class MarkdownCodeblocksParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = MarkdownCodeblocksParser()
        self.two_line = '''    line1
    line2'''
        self.text_code_text = '''text

    code

text'''
        self.code_text_code = '''    code1

text

    code2\n'''
        self.code_text_code_no_blank_lines = '''    code1
text
    code2'''
        self.with_content_type = '''    Content-Type: text/x-python
    line2'''

    def test_get_codeblock_on_empty(self):
        self.assertEqual(None, self.parser.get_codeblock('', 1))

    def test_get_codeblock_no_codeblocks(self):
        self.assertEqual(None, self.parser.get_codeblock('foo', 1))

    def test_get_codeblock_n_out_of_range(self):
        self.assertEqual(None, self.parser.get_codeblock('', 0))
        self.assertEqual(None, self.parser.get_codeblock('', -1))
        self.assertEqual(None, self.parser.get_codeblock('', 1))
        self.assertEqual(None, self.parser.get_codeblock('foo', 0))
        self.assertEqual(None, self.parser.get_codeblock('foo', -1))
        self.assertEqual(None, self.parser.get_codeblock('foo', 1))
        self.assertEqual(None, self.parser.get_codeblock('    foo', 0))
        self.assertEqual(None, self.parser.get_codeblock('    foo', -1))
        self.assertEqual(None, self.parser.get_codeblock('    foo', 2))

    def test_get_codeblock(self):
        self.assertEqual('    foo', self.parser.get_codeblock('    foo', 1).get_text())
        self.assertEqual('foo', self.parser.get_codeblock('    foo', 1).get_code())
        self.assertEqual(self.two_line,
            self.parser.get_codeblock(self.two_line, 1).get_text())
        expect_twoline = '''line1
line2'''
        self.assertEqual(expect_twoline,
            self.parser.get_codeblock(self.two_line, 1).get_code())
        self.assertEqual('    code\n\n',
            self.parser.get_codeblock(self.text_code_text, 1).get_text())
        self.assertEqual('code\n\n',
            self.parser.get_codeblock(self.text_code_text, 1).get_code())
        self.assertEqual('    code1\n\n',
            self.parser.get_codeblock(self.code_text_code, 1).get_text())
        self.assertEqual('code1\n\n',
            self.parser.get_codeblock(self.code_text_code, 1).get_code())
        self.assertEqual('    code2\n',
            self.parser.get_codeblock(self.code_text_code, 2).get_text())
        self.assertEqual('code2\n',
            self.parser.get_codeblock(self.code_text_code, 2).get_code())
        self.assertEqual('    code1\n',
            self.parser.get_codeblock(self.code_text_code_no_blank_lines, 1).get_text())
        self.assertEqual('code1\n',
            self.parser.get_codeblock(self.code_text_code_no_blank_lines, 1).get_code())
        self.assertEqual('    code2',
            self.parser.get_codeblock(self.code_text_code_no_blank_lines, 2).get_text())
        self.assertEqual('code2',
            self.parser.get_codeblock(self.code_text_code_no_blank_lines, 2).get_code())

    def test_get_codeblock_with_content_type(self):
        self.assertEqual('text/x-python',
            self.parser.get_codeblock(self.with_content_type, 1).content_type)
        self.assertEqual('    line2',
            self.parser.get_codeblock(self.with_content_type, 1).get_text())
        self.assertEqual('line2',
            self.parser.get_codeblock(self.with_content_type, 1).get_code())

    def test_parse_text_code_text(self):
        sections = self.parser.parse(self.text_code_text)
        self.assertEqual(3, len(sections))
        self.assert_(not sections[0].is_codeblock())
        self.assertEqual('text\n\n', sections[0].get_text())
        self.assert_(sections[1].is_codeblock())
        self.assertEqual('    code\n\n', sections[1].get_text())
        self.assertEqual('code\n\n', sections[1].get_code())
        self.assert_(not sections[2].is_codeblock())
        self.assertEqual('text', sections[2].get_text())

    def test_parse_code_text_code(self):
        sections = self.parser.parse(self.code_text_code)
        self.assertEqual(3, len(sections))
        self.assert_(sections[0].is_codeblock())
        self.assertEqual('    code1\n\n', sections[0].get_text())
        self.assertEqual('code1\n\n', sections[0].get_code())
        self.assert_(not sections[1].is_codeblock())
        self.assertEqual('text\n\n', sections[1].get_text())
        self.assert_(sections[2].is_codeblock())
        self.assertEqual('    code2\n', sections[2].get_text())
        self.assertEqual('code2\n', sections[2].get_code())
