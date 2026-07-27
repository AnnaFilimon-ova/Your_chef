import os
import telebot
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from db import create_table, get_blacklist, add_ingredient, remove_ingredient
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

create_table()

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyboard.add(KeyboardButton("Meal"))
reply_keyboard.add(KeyboardButton("BlackList"))
reply_keyboard.add(KeyboardButton("Delete BlackList"))

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Welcome!\nChoose an option:",
        reply_markup=reply_keyboard
    )

@bot.message_handler(func=lambda message: True)
def menu(message):
    if message.text == "Meal":
        recipe = get_meal(message.from_user.id)

        if recipe is None:
            bot.send_message(
                message.chat.id,
                "Couldn't find a meal without your blacklisted ingredients."
            )
            return
        bot.send_photo(message.chat.id, recipe["image"])
        bot.send_message(message.chat.id, format_meal(recipe))

    elif message.text == "BlackList":
        show_blacklist(message.chat.id, message.from_user.id)
        msg = bot.send_message(
            message.chat.id,
            "Enter an ingredient to add:"
        )
        bot.register_next_step_handler(msg, add_blacklist_ingredient)

    elif message.text == "Delete BlackList":
        show_blacklist(message.chat.id, message.from_user.id)
        msg = bot.send_message(
            message.chat.id,
            "Enter an ingredient to delete:"
        )
        bot.register_next_step_handler(msg, delete_blacklist_ingredient)

def show_blacklist(chat_id, user_id):
    blacklist = get_blacklist(user_id)

    if blacklist:
        bot.send_message(
            chat_id,
            "Your Black List:\n\n" + "\n".join(blacklist)
        )
    else:
        bot.send_message(
            chat_id,
            "Your Black List is empty."
        )

def add_blacklist_ingredient(message):
    if message.text.startswith("/"):
        return

    ingredient = message.text.strip().lower()
    if not ingredient:
        bot.send_message(message.chat.id, "Ingredient cannot be empty.")
        return

    if ingredient.lower() in (
        "meal",
        "blacklist",
        "delete blacklist"
    ):
        return

    add_ingredient(message.from_user.id, ingredient)

    blacklist = get_blacklist(message.from_user.id)
    if ingredient in blacklist:
        bot.send_message(
            message.chat.id,
            f'"{ingredient}" is already in your blacklist.'
        )
        return
    
    bot.send_message(
        message.chat.id,
        f'"{ingredient}" added.'
    )

    show_blacklist(message.chat.id, message.from_user.id)

def delete_blacklist_ingredient(message):
    if message.text.startswith("/"):
        return

    ingredient = message.text.strip().lower()
    if not ingredient:
        bot.send_message(message.chat.id, "Ingredient cannot be empty.")
        return

    if ingredient.lower() in (
        "meal",
        "blacklist",
        "delete blacklist"
    ):
        return

    remove_ingredient(message.from_user.id, ingredient)

    bot.send_message(
        message.chat.id,
        f'"{ingredient}" removed.'
    )

    show_blacklist(message.chat.id, message.from_user.id)

def get_meal(user_id):
    blacklist = [i.lower() for i in get_blacklist(user_id)]
    for _ in range(50):
        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/random.php",
                timeout=10
            )

            response.raise_for_status()
            meal = response.json()["meals"][0]

        except Exception:
            return None

        ingredients = []
        blocked = False

        for i in range(1, 21):

            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")

            if ingredient and ingredient.strip():

                ingredient_name = ingredient.strip().lower()

                if ingredient_name in blacklist:
                    blocked = True
                    break

                ingredients.append(
                    f"{measure.strip() if measure else ''} {ingredient}".strip()
                )

        if blocked:
            continue

        return {
            "name": meal["strMeal"],
            "ingredients": ingredients,
            "instructions": meal["strInstructions"],
            "image": meal["strMealThumb"]
        }

    return None

def format_meal(recipe):
    text = f"Name: {recipe['name']}\n\n"
    text += "Ingredients:\n"
    for i, ingredient in enumerate(recipe["ingredients"], 1):
        text += f"{i}. {ingredient}\n"
    text += "\nInstructions:\n"
    text += recipe["instructions"]
    return text

bot.polling(none_stop=True)