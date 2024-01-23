import sqlite3


def retrieve_history(identifier):
    database = sqlite3.connect("../storage/chat_database.db")
    cursor = database.cursor()

    if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'").fetchone():
        cursor.execute("CREATE TABLE chat_history (identifier text, sender text, message text)")
        database.commit()

    cursor.execute("SELECT * FROM chat_history WHERE identifier = ?", [identifier])

    history = cursor.fetchall()
    database.close()

    return history


def write_history(identifier, sender, message):
    database = sqlite3.connect("../storage/chat_database.db")
    cursor = database.cursor()

    cursor.execute("INSERT INTO chat_history VALUES (?, ?, ?)", (identifier, sender, message))
    database.commit()
    database.close()
