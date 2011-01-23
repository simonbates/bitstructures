from django import template
from django.utils.tzinfo import LocalTimezone
from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype
from pygments.formatters import HtmlFormatter
from bitstructures.substructure.codeblocks import MarkdownCodeblocksParser

def rfc3339(dt):
    if dt.tzinfo == None:
        dt_out = dt.replace(tzinfo=LocalTimezone(dt), microsecond=0)
    else:
        dt_out = dt.replace(microsecond=0)
    return dt_out.isoformat()

def syntax_highlighted_markdown(markdown_text):
    parser = MarkdownCodeblocksParser()
    formatter = HtmlFormatter()
    sections = parser.parse(markdown_text)
    for_markdown = list()
    html = list()
    for section in sections:
        if section.is_codeblock() and section.content_type:
            # run Markdown on any text that isn't to be syntax highlighted
            if for_markdown:
                html.append(markdown(''.join(for_markdown)))
                for_markdown = list()
            # run Pygments on code to be syntax highlighted
            html.append(highlight(section.get_code(),
                get_lexer_for_mimetype(section.content_type), formatter))
        else:
            for_markdown.append(section.get_text())
    # run Markdown on any remaining text that isn't to be syntax highlighted
    if for_markdown:
        html.append(markdown(''.join(for_markdown)))
    return ''.join(html)

register = template.Library()
register.filter('rfc3339', rfc3339)
register.filter('syntax_highlighted_markdown', syntax_highlighted_markdown)
