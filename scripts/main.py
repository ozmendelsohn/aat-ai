fro
import json

# Read the Open AI API key from the secret file
with open("secret.json") as f:
    secret = json.load(f)
    open_ai_key = secret["open_ai_key"]

openai_conversation = LLMChat()
openai_conversation.view()