import re

class MarkdownParser:
    """
    Utility class for parsing markdown text and extracting code blocks.
    """
    
    @classmethod
    def get_code_block(cls, markdown_text: str, language: str = None) -> str:
        """
        Extract code of a specific language from a markdown string.

        Parameters
        ----------
        markdown_text : str
            Markdown text with code enclosed in ```language and ```.
        language : str, optional
            The programming language of the code. This is used to find the correct delimiter.
            If not provided, it will look for any code block regardless of the language.

        Returns
        -------
        str
            Extracted code. Returns an empty string if no code is found.
        """
        if language is None:
            language = cls.get_language(markdown_text)

        pattern = f"```{language}(.*?)```"

        matches = re.findall(pattern, markdown_text, re.DOTALL | re.MULTILINE)
        return matches[0].strip() if matches else ""

    @classmethod
    def get_language(cls, markdown_text: str) -> str:
        """
        Detect the programming language of a code block in a markdown string.

        Parameters
        ----------
        markdown_text : str
            Markdown text with code enclosed in ```language and ```.

        Returns
        -------
        str
            Detected programming language. Returns an empty string if no language is detected.
        """
        pattern = r"```(\w+)\n"
        match = re.search(pattern, markdown_text)
        return match.group(1) if match else ""
    
    @classmethod
    def get_result(cls, markdown_text:str) -> dict:
        """
        Returns the result of the code block in a markdown string as a dictionary.
        
        Parameters
        ----------
        markdown_text : str
            Markdown text with code enclosed in ```language and ```.
            
        Returns
        -------
        dict
            Dictionary with the keys 'code' and 'language'.
        """
        code = cls.get_code_block(markdown_text)
        language = cls.get_language(markdown_text)
        return {'code': code, 'language': language}
