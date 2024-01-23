import os
import mysql.connector


def transform_data(cars, car_addons, addon_categories):
    """
    Transforms the database data into a query for the GPT prompt
    :param list cars:
    :param list car_addons:
    :param list addon_categories:
    :return:
    """

    car_data = {}
    categories = {}

    for category in addon_categories:
        categories[category[0]] = {
            'name': category[1]
        }

    for car in cars:
        car_data[car[0]] = {
            'id': car[0],
            'name': car[1],
            'model': car[2],
            'year': car[3],
            'type': car[4],
            'drivetrain': car[5],
            'addons': {}
        }

        for category in addon_categories:
            car_data[car[0]]['addons'][category[1]] = []

    for addon in car_addons:
        car_data[addon[1]]['addons'][categories[addon[2]]['name']].append({
            'name': addon[3],
        })

    car_stock_string = ""

    for car in car_data:
        if car_stock_string != "":
            car_stock_string += "---\n"
        car_stock_string += f"{car_data[car]['name']} {car_data[car]['model']} from {car_data[car]['year']}.\n"
        car_stock_string += f"It is a {car_data[car]['type']}.\n"
        car_stock_string += f"It is driven by {car_data[car]['drivetrain']}\n"
        car_stock_string += f"It has the following addons:\n"

        for category in car_data[car]['addons']:
            car_stock_string += f"{category}:\n"

            for addon in car_data[car]['addons'][category]:
                car_stock_string += f"- {addon['name']}\n"

    prompt = f"""You are working in a car dealership. Information about all the cars in our stock is provided in the Context section of the question. Your main job is to help a customer end up with a car model that would fit his needs. You should ask for more information about what type of car the person wants, but you should not exceed the information given in the context.

Do not reply with any information that is not from our context. If you don't know what the customer meant - ask for more details, but never trust any other source than our Context. Addons are "perks" on the car, not modifications. These come as standard from factory

Keep answers short and direct, make them seem like a salesman

---

Context:

{car_stock_string}
---
"""
    if not os.path.exists('../storage'):
        os.mkdir('../storage')

    with open('../storage/prompt.txt', 'w') as file:
        file.write(prompt)
        file.close()


def load_database():
    connector = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_DATABASE')
    )

    cars_query = connector.cursor()
    cars_query.execute("SELECT * FROM cars")
    cars = cars_query.fetchall()

    addons_query = connector.cursor()
    addons_query.execute("SELECT * FROM car_addons")
    car_addons = addons_query.fetchall()

    addon_categories_query = connector.cursor()
    addon_categories_query.execute("SELECT * FROM addon_categories")
    addon_categories = addon_categories_query.fetchall()

    connector.close()

    transform_data(cars, car_addons, addon_categories)


def get_prompt_template_from_database():
    """
    Get the dataset from the database file
    """
    # Check if dataset file exists, if not, create it
    if not os.path.exists('../storage/prompt.txt'):
        load_database()

    with open('../storage/prompt.txt', 'r') as file:
        return file.read()
