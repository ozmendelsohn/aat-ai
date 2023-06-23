import panel as pn
import re
from utils.parsers import MarkdownParser
pn.extension('codeeditor')

class TextCodeRow(pn.Column):
    """
    A class for displaying a row of text and code.

    Parameters
    ----------
    text : str
        The text to display in the row.
    """

    def __init__(self, text: str):
        super().__init__()
        # Split the text into blocks using ``` as the delimiter
        blocks = text.split('```')
        for i, block in enumerate(blocks):
            # If the block index is even, it's a text block
            if i % 2 == 0:
                if block.strip() != '':
                    self.append(pn.widgets.StaticText(value=block.strip()))
            # If the block index is odd, it's a code block
            else:
                self.append(pn.widgets.CodeEditor(value=MarkdownParser.get_code_block('```' + block + '```'), 
                                                  language=MarkdownParser.get_language('```' + block + '```'),
                                                  theme='dracula',
                                                  sizing_mode='stretch_width',
                                                  min_height=100,
                                                  min_width=500))
