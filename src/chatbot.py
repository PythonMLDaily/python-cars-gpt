import ai_engine
import chat_history


def make_ai_request(question, identifier):
    # Find the chat log in SQlite database
    history = chat_history.retrieve_history(identifier)
    # If the chat log is more than 1 message, add the chat history to the prompt
    chat_messages = ""

    if len(history) > 1:
        chat_messages = "Chat history:" + '\n'.join([f'{message[1]}: {message[2]}\n' for message in history])
        # Add the chat history to the prompt

    chat_history.write_history(identifier, "user", question)

    ai_response = ai_engine.generate_response(question, chat_messages)

    chat_history.write_history(identifier, "assistant", ai_response)

    return ai_response
