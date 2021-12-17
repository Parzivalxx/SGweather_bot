import os
import logging
from helper import *
from telegram.ext import Updater
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

PORT = int(os.environ.get('PORT', 5000))

bot_token = ''
geocode_token = ''
heroku_site = ''
forecast_field = "2-hour-weather-forecast"
fields = ["air-temperature", "rainfall", "relative-humidity", "wind-direction", "wind-speed"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id,
    text=f"Hi {name}! Welcome to the SGweather_bot.\nSimply enter @SG_weatherbot and a postal code to view current and forecast weather info.")

def get_text(msg):
    current_weather = ""
    postal_code = msg
    coords, address = get_info_from_postal(postal_code)
    forecast_json = get_json(forecast_field)
    nearest_area = get_nearest_area(coords, forecast_json)
    weather_forecast = get_forecast_for_area(nearest_area, forecast_json)
    for field in fields:
        weather_val = get_weather_val(coords, field)
        current_weather += f"{field}: {weather_val}\n"
    weather = f"Postal code: {msg}\nAddress: {address}\nNearest area: {nearest_area}\n\nCurrent weather:\n{current_weather}\nForecast weather: {weather_forecast}"
    return weather

def show_correct_usage(update: Update, context: CallbackContext):
    msg = "To use me, simply enter @SG_weatherbot and a postal code to view current and forecast weather info."
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

def inline_get_weather(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='get weather info',
            input_message_content=InputTextMessageContent(get_text(query))
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    correct_usage_handler = MessageHandler(filters = (Filters.text), callback = show_correct_usage)
    dispatcher.add_handler(correct_usage_handler)

    inline_weather_handler = InlineQueryHandler(callback = inline_get_weather, pattern = "\d\d\d\d\d\d")
    dispatcher.add_handler(inline_weather_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=bot_token,
                          webhook_url=heroku_site + bot_token)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()