from dotenv import load_dotenv

import chatbot

# Load the .env file to be able to use the secrets
load_dotenv()

# print(chatbot.make_ai_request("What cars do you have in stock?", '#2'))
print(chatbot.make_ai_request("Which of them has heated seats?", '#2'))
