import database
import chat_history
from openai import OpenAI


def make_ai_request(question, identifier):
    messages_list = []

    prompt = database.get_prompt_template_from_database()

    messages_list.append({"role": "system", "content": prompt})

    # Find the chat log in SQlite database
    history = chat_history.retrieve_history(identifier)
    # If the chat log is more than 1 message, add the chat history to the prompt
    if len(history) > 1:
        messages_list.append({"role": "system",
                              "content": f"Chat history: {''.join([f'{message[1]}: {message[2]}\n' for message in history])}"})
        # Add the chat history to the prompt

    messages_list.append({"role": "user", "content": question})

    # Prompt needs to be a LIST :(
    """
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Knock knock."},
        {"role": "assistant", "content": "Who's there?"},
        {"role": "user", "content": "Orange."},
    ]
    """

    chat_history.write_history(identifier, "user", question)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_list,
    )

    ai_response = response.choices[0].message.content.strip()

    chat_history.write_history(identifier, "assistant", ai_response)

    return ai_response
