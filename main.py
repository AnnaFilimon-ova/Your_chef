import requests
import os
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(token=TOKEN)

reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyboard.add(KeyboardButton("Meal"))

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Click the button", reply_markup=reply_keyboard)

@bot.message_handler(func=lambda message: True)
def check_button(message):
    if message.text == "Meal":
        meal_text = print_meal()
        bot.reply_to(message, meal_text)

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

def print_meal():
    recipe = get_meal()
    text = f"Name: {recipe["name"]} \n"
    text += "\nIngredients: \n"
    for item in recipe["ingredients"]:
        text += f"- {item} \n"

    text +="\nInstructions:"
    text += f"{recipe['instructions']}"
    return text

bot.polling()