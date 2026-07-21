import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

def get_meal():
    url = "https://www.themealdb.com/api/json/v1/1/random.php"

    response = requests.get(url)
    meal = response.json()["meals"][0]

    ingredients = []

    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():
            ingredients.append(f"{measure} {ingredient}")

    return {
        "name": meal["strMeal"],
        "ingredients": ingredients,
        "instructions": meal["strInstructions"]
    }

#Start work
start = input("Do you want starting? (start/q) ")

if start == "start":
    recipe = get_meal()

    if recipe:
        print("Name:", recipe["name"])
        print("\nIngredients:")
        for item in recipe["ingredients"]:
            print("-", item)

        print("\nInstructions:")
        print(recipe["instructions"])

elif start == "q":
    print("Goodbye")

else:
    print("Value error")
