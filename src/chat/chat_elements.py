import panel as pn
import re
from utils.parsers import MarkdownParser
from utils.run_time import BaseCodeRunTime
pn.extension('codeeditor', 'plotly', 'katex')

class TextCodeRow(pn.Column):
    """
    A class for displaying a row of text and code.

    Parameters
    ----------
    text : str
        The text to display in the row.
    code_run_time : BaseCodeRunTime
        The code run time object to run the code with.
    """
    width_padding = 40
    height_padding = 40

    def __init__(self, text: str, code_run_time: BaseCodeRunTime = None):
        super().__init__()
        self.code_run_time = code_run_time
        # Split the text into blocks using ``` as the delimiter
        blocks = text.split('```')
        for i, block in enumerate(blocks):
            # If the block index is even, it's a text block
            if i % 2 == 0:
                if block.strip() != '':
                    self.append(pn.widgets.StaticText(value=block.strip()))
            else: # If the block index is odd, it's a code block
                code = MarkdownParser.get_code_block('```' + block + '```')
                language = MarkdownParser.get_language('```' + block + '```')
                width, height = self._get_code_size(code)
                self.append(self._get_code_widget(code, language, height, width))
                    
    def _get_code_size(self, code: str):
        """
        Get the size of the code block.

        Parameters
        ----------
        code : str
            The code block to get the size of.

        Returns
        -------
        Tuple[int, int]
            The width and height of the code block.
        """
        width = max([len(line) for line in code.split('\n')]) * 10 + self.width_padding
        height = len(code.split('\n')) * 20 + self.height_padding
        return width, height
    
    def _get_code_widget(self, code: str, language: str, height: int, width: int) -> pn.viewable.Viewable:
        """
        Get the code widget.
        
        Parameters
        ----------
        code : str
            The code block to display.
        language : str
            The language of the code block.
        height : int
            The height of the code block.
        width : int
            The width of the code block.
        
        Returns
        -------
        pn.viewable.Viewable
            The code widget.
        """
        if language == 'python':
            return PythonCodeBlock(code, 
                                   code_width=width, 
                                   code_height=height, 
                                   code_run_time=self.code_run_time)
        else:
            return pn.widgets.Code(value=code, language=language, height=height, width=width)
                

class PythonCodeBlock(pn.Column):
    """
    A class for displaying a block of Python code, run button, and output.

    Parameters
    ----------
    code : str
        The code to display in the block.
    code_width : int
        The width of the code block.
    code_height : int
        The height of the code block.
    code_run_time : BaseCodeRunTime
        The code run time object to run the code with.
    """
    def __init__(self, 
                 code: str, 
                 code_width: int = None, 
                 code_height: int = None, 
                 code_run_time: BaseCodeRunTime = None):
        super().__init__()
        self.code = code
        self.code_run_time = code_run_time
        self.run_button = pn.widgets.Button(name='Run', button_type='primary')
        self.code_widget = pn.widgets.CodeEditor(value=self.code, 
                                                 language='python',
                                                 theme='dracula',
                                                 height=code_height,
                                                 width=code_width,
                                                 )
        self.append(self.code_widget)
        self.append(self.run_button)
        self.run_button.on_click(self.run)
        self.output_start_index = 2

    def run(self, event):
        """
        Run the Python code.

        Parameters
        ----------
        event : panel.io.events.Event
            The event object. Not used, but required by Panel's on_click function.
        """
        # Check code_run_time is not None
        if self.code_run_time is None:
            self.run_button.disabled = True
            self.run_button.name = 'No Run Time'
            return
        
        # Clear previous outputs
        while len(self) > self.output_start_index:
            self.pop(self.output_start_index) 
        try:
            # Run the code and get the outputs
            outputs = self.code_run_time.run_code(self.code_widget.value)
            
            if not isinstance(outputs, tuple):
                outputs = (outputs,)
            
            # Display the outputs
            for output in outputs:
                if isinstance(output, str):
                    self.append(pn.widgets.StaticText(value=output))
                elif isinstance(output, (dict, list)):
                    self.append(pn.pane.JSON(output))
                else:
                    self.append(output)

        except Exception as e:
            # If any error occurs, display the error message
            self.append(pn.pane.Alert(str(e), alert_type='danger'))

    
    def _get_code_size(self, code: str):
        """
        Get the size of the code block.

        Parameters
        ----------
        code : str
            The code block to get the size of.

        Returns
        -------
        Tuple[int, int]
            The width and height of the code block.
        """
        width = max([len(line) for line in code.split('\n')]) * 10 + self.width_padding
        height = len(code.split('\n')) * 20 + self.height_padding
        return width, height