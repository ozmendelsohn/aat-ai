from abc import ABC, abstractmethod
from langchain import PromptTemplate

class BasePromptTemplateCreator(ABC):
    """
    Base class for all PromptTemplate creators.

    This class outlines the structure for creating a PromptTemplate generator,
    including an abstract method for creating a PromptTemplate.
    """
    TEMPLATE = "Base template for all PromptTemplate creators."

    @abstractmethod
    def _create_prompt_template(self) -> PromptTemplate:
        """Abstract method that should be overwritten by subclasses to create a new PromptTemplate.

        Returns
        -------
        PromptTemplate
            The newly created PromptTemplate.
        """
        pass

    @abstractmethod
    def get_prompt(self) -> PromptTemplate:
        """Returns an updated prompt template.

        Returns
        -------
        PromptTemplate
            The updated PromptTemplate.
        """
        pass
    
    
