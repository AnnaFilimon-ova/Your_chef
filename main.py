import requests
import os
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from db import create_table, get_blacklist, add_ingredient

create_table()

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(token=TOKEN)

reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyboard.add(KeyboardButton("Meal"))
reply_keyboard.add(KeyboardButton("BlackList"))

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome! \nClick the button, please", reply_markup=reply_keyboard)

@bot.message_handler(func=lambda message: True)
def check_button(message):
    if message.text == "Meal":
        recipe = get_meal()
        meal_text = format_meal(recipe)

        bot.send_photo(
            message.chat.id,
            recipe["image"]
        )

        bot.send_message(
            message.chat.id,
            meal_text
        )

    elif message.text == "BlackList":
        user_id = message.from_user.id
        blacklist = get_blacklist(user_id)

        if blacklist:
            bot.send_message(
                message.chat.id,
                "Your Black List:\n " + "\n".join(blacklist)
            )
        else:
            bot.send_message(
                message.chat.id,
                "Your Black List is empty."
            )

        bot.send_message(
            message.chat.id,
            "Enter the ingredient: "
        )
        bot.register_next_step_handler(
            message,
            add_blacklist_ingredient
        )

def add_blacklist_ingredient(message):
    user_id = message.from_user.id
    ingredient = message.text.lower()

    add_ingredient(user_id, ingredient)
    bot.send_message(
        message.chat.id,
        f"Your added {ingredient}."
    )
    blacklist = get_blacklist(user_id)

    bot.send_message(
        message.chat.id,
        "Your Black List:\n " + "\n".join(blacklist)
    )


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
        "instructions": meal["strInstructions"],
        "image": meal["strMealThumb"]
    }

def format_meal(recipe):
    text = f"Name: {recipe['name']}\n\n"

    text += "Ingredients:\n"
    for index, item in enumerate(recipe["ingredients"], start=1):
        text += f"{index} - {item}\n"

    text += "\nInstructions:\n"
    text += recipe["instructions"]

    return text

bot.polling()