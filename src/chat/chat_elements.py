from typing import Tuple
import panel as pn
from utils.parsers import MarkdownParser
from run_time import BaseCodeRunTime
pn.extension('codeeditor', 'plotly')


class BaseChatElement(pn.Column):
    
    def __init__(self):
        super().__init__()

    def get_information(self) -> str:
        """
        Get the information from the chat element ready for to add the the LLMs memory.

        Returns
        -------
        str
        """
        pass

class TextRow(BaseChatElement):
    def __init__(self, text: str, max_width_chars: int = 60, char_width: int = 6, char_height: int = 20):
        """
        Initialize the TextRow object.

        Parameters
        ----------
        text : str
            The text to be displayed.
        max_width_chars : int, optional
            The maximum width of the text row, in characters, default is 60.
        char_width : int, optional
            The estimated pixel width of a character, default is 10.
        char_height : int, optional
            The estimated pixel height of a character, default is 20.
        """
        super().__init__()
        self.text = text
        self.max_width_chars = max_width_chars
        self.char_width = char_width
        self.char_height = char_height
        width, height = self.calculate_dimensions()
        self.append(pn.widgets.StaticText(value=self.text, width=width, height=height))

    def calculate_dimensions(self) -> Tuple[int, int]:
        """
        Calculate the width and height of the text block in pixels.

        Returns
        -------
        int
            The width of the text block.
        int
            The height of the text block.
        """
        lines = len(self.text) // self.max_width_chars + 1
        width = self.max_width_chars * self.char_width
        height = lines * self.char_height
        return width, height

    def get_information(self) -> str:
        """
        Get the information from the chat element ready for to add the the LLMs memory.
        
        Returns
        -------
        str
            The information from the chat element.
        """
        return self.text


class TextCodeRow(BaseChatElement):
    """
    A class for displaying a row of text and code.

    Parameters
    ----------
    text : str
        The text to display in the row.
    run_time : BaseCodeRunTime
        The code run time object to run the code with.
    """
    width_padding = 40
    height_padding = 40

    def __init__(self, text: str, run_time: BaseCodeRunTime = None):
        super().__init__()
        self.run_time = run_time
        # Split the text into blocks using ``` as the delimiter
        blocks = text.split('```')
        for i, block in enumerate(blocks):
            # If the block index is even, it's a text block
            if i % 2 == 0:
                if block.strip() != '':
                    self.append(pn.widgets.StaticText(value=block.strip()))
            else:  # If the block index is odd, it's a code block
                code = MarkdownParser.get_code_block('```' + block + '```')
                language = MarkdownParser.get_language('```' + block + '```')
                self.append(self._get_code_widget(code, language))


        # add a divider between each text/code block in the row
        for i in range(len(self.objects) - 1):
            self.insert(i * 2 + 1,pn.layout.Divider())
            

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

    def _get_code_widget(self, code: str, language: str) -> pn.viewable.Viewable:
        """
        Get the code widget.

        Parameters
        ----------
        code : str
            The code block to display.
        language : str
            The language of the code block.

        Returns
        -------
        pn.viewable.Viewable
            The code widget.
        """
        width, height = self._get_code_size(code)
        if language == 'python':
            return PythonCodeBlock(code,
                                   run_time=self.run_time)
        else:
            return pn.widgets.CodeEditor(value=code, language=language, height=height, width=width)

    def get_information(self) -> str:
        """
        Get the information from the chat element ready for to add the the LLMs memory.

        Returns
        -------
        str
            The information from the chat element.
        """
        information = ''
        for element in self.objects:
            if isinstance(element, pn.widgets.StaticText):
                information += '\n\n' + element.value
            elif isinstance(element, pn.widgets.CodeEditor):
                language = element.language
                code = element.value
                markdown_code = f'```{language}\n{code}\n```'
                information += '\n\n' + markdown_code
            elif isinstance(element, BaseChatElement):
                information += '\n\n' + element.get_information()
        return information[2:]  # remove the first two new lines


class PythonCodeBlock(BaseChatElement):
    """
    A class for displaying a block of Python code, run button, and output.

    Parameters
    ----------
    code : str
        The code to display in the block.
    run_time : BaseCodeRunTime
        The code run time object to run the code with.
    """
    height_padding = 20
    width_padding = 20

    def __init__(self,
                 code: str,
                 run_time: BaseCodeRunTime = None):
        super().__init__()
        self.code = code
        self.run_time = run_time
        self.run_button = pn.widgets.Button(name='Run', button_type='primary')
        width, height = self._get_code_size(code)

        self.code_widget = pn.widgets.CodeEditor(value=self.code,
                                                 language='python',
                                                 theme='dracula',
                                                 height=height,
                                                 width=width,
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
        # Check run_time is not None
        if self.run_time is None:
            self.run_button.disabled = True
            self.run_button.name = 'No Run Time'
            return

        # Clear previous outputs and save the descriptions in a cache
        description_cache = {}
        for i in list(range(self.output_start_index, len(self.objects)))[::-1]:
            old_widget = self.pop(i)
            if isinstance(old_widget, PythonObjDescription):
                description_cache[i] = old_widget.description.value
        try:
            # Run the code and get the outputs
            outputs = self.run_time.run_code(self.code_widget.value)

            if not isinstance(outputs, tuple):
                outputs = (outputs,)

            # Display the outputs
            for output in outputs:
                if isinstance(output, str):
                    self.append(pn.widgets.StaticText(value=output))
                elif isinstance(output, (dict, list)):
                    self.append(pn.pane.JSON(output))
                else:
                    self.append(PythonObjDescription(output))

        except Exception as e:
            # If any error occurs, display the error message
            self.append(pn.pane.Alert(f'{type(e).__name__}: {str(e)}', alert_type='danger'))
            
        # Add the descriptions back from the cache
        for i, description in description_cache.items():
            if isinstance(self.objects[i], PythonObjDescription):
                self.objects[i].set_description(description)

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

    def get_information(self) -> str:
        """
        Get the information from the chat element ready for to add the the LLMs memory.

        Returns
        -------
        str
            The information from the chat element.
        """
        information = ''
        for element in self.objects:
            if isinstance(element, pn.widgets.StaticText):
                information += '\n' + element.value
            elif isinstance(element, (pn.pane.Alert, pn.pane.JSON)):
                information += '\n' + element.object
            elif isinstance(element, pn.widgets.CodeEditor):
                language = element.language
                code = element.value
                markdown_code = f'```{language}\n{code}\n```'
                information += '\n' + markdown_code
            elif isinstance(element, pn.widgets.TextInput):
                information += '\nUser input: ' + element.value
            elif isinstance(element, BaseChatElement):
                information += '\n' + element.get_information()
            elif isinstance(element, pn.widgets.Button):
                continue
            else:
                information += '\n' + 'Generated figure of type: ' + str(type(element))

        return information[1:]  # remove the first new line


class PythonObjDescription(BaseChatElement):
    """
    A class for displaying a Python object and add a editable description.

    Parameters
    ----------
    Object : any
        The object to display.
    """

    def __init__(self, Object: any):
        super().__init__()
        self.object = Object
        self.description = pn.widgets.TextInput(name='Description',
                                                value='',
                                                placeholder='Input a description for the object, will be added to the LLMs memory, as most LLMs are only able to store text.')
        self.hide_button = pn.widgets.Button(name="Hide", width=100)
        self.hide_button.on_click(self.toggle_visibility)
        self.is_hidden = False
        
        self.append(self.hide_button)
        self.append(self.object)
        self.append(self.description)


        self.height = 600
        self.width = 600
        

    def get_information(self) -> str:
        """
        Get the information from the chat element ready for to add the the LLMs memory.

        Returns
        -------
        str
            The information from the chat element.
        """
        information = 'Generate figure of type: ' + str(type(self.object))
        if self.description.value != '':
            information += '\nUser description: ' + self.description.value
        return information
    
    def get_description(self) -> str:
        """
        Get the description from the chat element ready for to add the the LLMs memory.

        Returns
        -------
        str
            The description from the chat element.
        """
        return self.description.value
    
    def set_description(self, description: str) -> None:
        """
        Set the description of the chat element.

        Parameters
        ----------
        description : str
            The description to set.
        """
        self.description.value = description

    def toggle_visibility(self, event):
        """
        Toggle the visibility of the object and description fields.

        Parameters
        ----------
        event : str
            The button click event.
        """
        if self.is_hidden:
            self.objects = [self.hide_button, self.object, self.description]
            self.hide_button.name = "Hide"
        else:
            self.objects = [self.hide_button, self.description]
            self.hide_button.name = "Unhide"

        self.is_hidden = not self.is_hidden

