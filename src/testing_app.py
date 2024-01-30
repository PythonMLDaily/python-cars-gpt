import uuid

from dotenv import load_dotenv
import chatbot

# Load the .env file to be able to use the secrets
load_dotenv()

print(chatbot.make_ai_request("Which cars are real wheel driven?", "a9d1f1c2-b897-4ba0-9b4b-dec9099ab94f"))
