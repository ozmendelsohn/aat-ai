from typing import List, Dict

import param
import panel as pn
from langchain.llms import OpenAI, BaseLLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from prompts import BasePromptTemplateCreator

pn.extension(template="bootstrap")


class StreamHandler(BaseCallbackHandler):
    """
    A handler for streaming the language model's output to a panel widget.

    Parameters
    ----------
    container : pn.widgets.ChatBox
        The chatbox container where the AI's responses will be appended.
    initial_text : str, optional
        The initial text to be displayed in the chat box.
    target_attr : str, optional
        The attribute of the container where the AI's responses will be displayed.

    """
    def __init__(self, container: pn.widgets.ChatBo, 
                 initial_text:str="", 
                 target_attr:str="value"):
        self.container = container
        self.text = initial_text
        self.target_attr = target_attr

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Callback function for handling new tokens from the language model.

        Parameters
        ----------
        token : str
            The new token received from the language model.
        """
        self.text += token
        self.container.replace(-1, {"AI": [self.text]})

# Define a class for handling conversations with any LLM
class LLMConversation(param.Parameterized):
        """
    A class for handling conversations with a language model.

    Parameters
    ----------
    llm : langchain.llms.BaseLLM
        The language model to use for the conversation.
    prompt_template_creator : BasePromptTemplateCreator, optional
        The prompt template creator for the conversation.
    verbose : bool, optional
        If True, print verbose output.
    """

    # Initialize the conversation handler
    def __init__(self, 
                 llm: BaseLLM, 
                 prompt_template_creator: BasePromptTemplateCreator = None,
                 verbose: bool = False,
                 **params):
        # Use the provided LLM
        self._llm = llm
        # Set up a conversation chain, which manages the flow of conversation
        # It uses a buffer memory to keep track of the conversation history
        self._chain = ConversationChain(
            memory=ConversationBufferMemory(), 
            llm=self._llm,
            verbose=verbose
        )
        if prompt_template_creator:
            self._chain.prompt = prompt_template_creator.get_prompt()
        # Set up a loading spinner to display while the AI is generating a response
        self._spinner = pn.indicators.LoadingSpinner(
            value=True,
            width=18,
            height=18,
        )
        # Set up a chat box widget for user input and AI responses
        self.chat_box = pn.widgets.ChatBox()
        # Set a watch on the chat box's value attribute to call the _chat method whenever the user sends a message
        self.chat_box.param.watch(self._chat, "value")

    # Decorator to disable the chat box while the AI is thinking
    def _disable_inputs(func):
        async def inner(self, *args, **kwargs):
            try:
                self.chat_box.disabled = True  # Disable the chat box
                await func(self, *args, **kwargs)  # Run the decorated function
            finally:
                self.chat_box.disabled = False  # Enable the chat box when the function is done

        return inner

    # @LLMConversation._disable_inputs
    async def _chat(self, event: Any) -> None:
        """
        Handle a chat event.

        Parameters
        ----------
        event : Any
            The chat event.
        """
        user_message = event.new[-1]  # Get the last message from the user
        input = user_message.get("You")  # Extract the user's input from the message
        if input is None:
            return  # If there's no input (e.g., the message was from the AI), do nothing
        self.chat_box.append({"AI": self._spinner})  # Show the loading spinner while the AI is generating a response
        # Attach the StreamHandler callback to the language model
        # We do this every time a message is received so that the StreamHandler starts with fresh text each time
        self._llm.callbacks = [StreamHandler(self.chat_box)]
        # Generate a response from the AI
        await self._chain.apredict(input=input)

    # Method for displaying the chat box in a Panel application
    def view(self) -> pn.widgets.ChatBox:
                """
        Return the chat box for display in a Panel application.

        Returns
        -------
        pn.widgets.ChatBox
            The chat box.
        """
        return self.chat_box.servable()  # Make the chat box servable so that it can be displayed in a Panel app



