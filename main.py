import requests

def get_recipe(meal_name):
    url = "https://www.themealdb.com/api/json/v1/1/search.php"

    response = requests.get(url, params={"s": meal_name})
    data = response.json()

    if not data.get("meals"):
        return None

    meal = data["meals"][0]

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
    meal = input("Enter meal name: ")

    recipe = get_recipe(meal)

    if recipe:
        print("Name:", recipe["name"])
        print("\nIngredients:")
        for item in recipe["ingredients"]:
            print("-", item)

        print("\nInstructions:")
        print(recipe["instructions"])
    else:
        print("Recipe not found")

elif start == "q":
    print("Goodbye")

else:
    print("Value error")
