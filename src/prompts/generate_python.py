from typing import Optional

from langchain import PromptTemplate

from prompts import BasePromptTemplateCreator


class EDAFunctionPromptTemplateCreator(BasePromptTemplateCreator):
    """
    A class used to generate and manage PromptTemplates for EDA functions.

    Attributes
    ----------
    libraries : str
        String representation of Python libraries.
    tables : str
        String representation of available tables.
    function_name : str
        Name of the function that the data scientist must write.

    Methods
    -------
    update_libraries(new_libraries: str) -> None:
        Updates the libraries attribute.
    update_tables(new_tables: str) -> None:
        Updates the tables attribute.
    get_prompt() -> PromptTemplate:
        Returns an updated prompt template.
    """

    TEMPLATE = """
You are a chatbot that has been trained to help data scientists perform exploratory data analysis.
Following is a conversation between you and a data scientist, provide a response to the data scientist's question.
You cannot use any libraries that are not provided in the libraries section.
You must write the code as a function that takes in the tables as arguments and returns a string, dictionary or figure or any tuple of them.
The function must be named {function_name}.
You cannot use any variables that are not provided in the tables section.
You cannot run the code, you can only write it.
When writing Python code you must use markdown notation, start with ```python and end with ```.
You have access to the following libraries:
{libraries}
Answer with the following table variables:
{tables}
Use the following history to help you answer the question:
{history}
Answer the following: {input}"""

    def __init__(
        self, libraries: str, tables: str, function_name: str = "eda_function"
    ):
        """
        Parameters
        ----------
        libraries : str
            String representation of Python libraries.
        tables : str
            String representation of available tables.
        function_name : str, optional
            Name of the function that the AI will create, by default "eda_function".
        """
        self.libraries = libraries
        self.tables = tables
        self.function_name = function_name

    def _create_prompt_template(self) -> PromptTemplate:
        """Creates a new PromptTemplate based on current libraries and tables.

        Returns
        -------
        PromptTemplate
            Newly created PromptTemplate.
        """
        template = self.TEMPLATE.format(
            libraries=self.libraries,
            tables=self.tables,
            function_name=self.function_name,
            history="{history}",
            input="{input}",
        )
        return PromptTemplate(input_variables=["history", "input"], template=template)

    def update_libraries(self, new_libraries: str) -> None:
        """Updates the libraries attribute.

        Parameters
        ----------
        new_libraries : str
            New string representation of Python libraries to update with.
        """
        self.libraries = new_libraries

    def update_tables(self, new_tables: str) -> None:
        """Updates the tables attribute.

        Parameters
        ----------
        new_tables : str
            New string representation of available tables to update with.
        """
        self.tables = new_tables

    def get_prompt(self) -> PromptTemplate:
        """Returns an updated prompt template.

        Returns
        -------
        PromptTemplate
            An updated PromptTemplate based on current libraries and tables.
        """
        return self._create_prompt_template()
