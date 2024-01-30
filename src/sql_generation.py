import json
import os
from openai import OpenAI
import mysql.connector
import database


def get_table_names():
    connector = database.connect()
    cars_query = connector.cursor()

    cars_query.execute("""
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM information_schema.columns
WHERE table_schema = DATABASE()
ORDER BY table_name, ordinal_position
""")
    tables = cars_query.fetchall()

    connector.close()

    table_data = {}
    for table in tables:
        table_data[table[0]] = table_data.get(table[0], [])
        table_data[table[0]].append({
            "name": table[1],
            "type": table[2]
        })

    return table_data


def query_safety_check(query):
    banned_actions = ['insert', 'update', 'delete', 'alter', 'drop', 'truncate', 'create', 'replace']

    if any(action in query for action in banned_actions):
        raise Exception("Query is not safe")


def query_open_ai(prompt, temperature=0.7):
    client = OpenAI()
    completions = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=100,
    )

    return completions.choices[0].message.content


def build_prompt(question, query=None, query_output=None, chat_messages=None):
    tables = get_table_names()

    table_prompt = ""
    for table in tables:
        table_prompt += f"{table} has columns: {', '.join([f'{column['name']} ({column['type']})' for column in tables[table]])}\n"

    history = ""
    if chat_messages and chat_messages != "":
        history = "\n" + chat_messages

    query_prompt = ""

    if query:
        query_prompt += "SQLQuery: " + query + "\n"
        if query_output:
            query_prompt += "SQLResult: " + query_output + "\n"
        rules = "Answer: "
    else:
        rules = ("(Your answer HERE must be a syntactically correct MySQL query with no extra information or "
                 "quotes.Omit SQLQuery: from your answer)")

    return f"""
    You are a salesman in a car dealership. Information about all the cars in our stock is provided in the Context section of the question. Your main job is to help a customer end up with a car model that would fit his needs. You should ask for more information about what type of car the person wants, but you should not exceed the information given in the context.
    
    Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer.
Use the following format:

---

Guidelines

Question: "User question here"
SQLQuery: "SQL Query used to generate the result (if applicable)"
SQLResult: "Result of the SQLQuery (if applicable)"
Answer: "Final answer here (You fill this in with the SQL query only)"

---

Context 

Only use the following tables and columns:

{table_prompt}
{history}

Question: "{question}"
{query_prompt}

---

{rules}
"""


def get_query(question):
    prompt = build_prompt(question)
    query = query_open_ai(prompt)
    query = query.strip()

    query_safety_check(query)

    return query


def evaluate_query(query):
    connector = database.connect()
    cars_query = connector.cursor()
    cars_query.execute(query)
    cars = [dict((cars_query.description[i][0], value) for i, value in enumerate(row)) for row in cars_query.fetchall()]
    connector.close()

    return json.dumps(cars, indent=4, default=str)


def generate(question, chat_messages=None):
    query = get_query(question)
    query_output = evaluate_query(query)
    retry_query_prompt = build_prompt(question, query, query_output, chat_messages=chat_messages)
    generated_query = query_open_ai(retry_query_prompt)

    return generated_query.strip().strip('"')