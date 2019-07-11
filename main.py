# -*- coding:utf-8 -*-

import telebot
from random import choice
import json

from db_models import Content, Themes, ContentCategory, User
from dbconnector import Session
from settings import *

import logging

logging.basicConfig(level=logging.DEBUG)

bot = telebot.AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_handler(message):
    user = User.get(message)
    if not user:
        user = User.create(message)
    bot.send_message(message.chat.id, 'Приветствую Вас, {username}'.format(username=user.username))

    categories = ContentCategory.list()
    start_keys = telebot.types.InlineKeyboardMarkup(3)
    start_keys.add(*[telebot.types.InlineKeyboardButton(text=c.category, callback_data=c.category) for c in categories])

    User.update_memory(message.chat.id, {'current_menu': 'categories'})
    bot.send_message(message.chat.id, 'Чего желаете?', reply_markup=start_keys)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    print('call', call)
    user_memory = User.read_memory(call.message.chat.id)
    print(user_memory)
    if user_memory.get('current_menu') == 'categories':
        User.update_memory(call.message.chat.id, {'selected_category': call.data})
        themes = Themes.list(call.data)
        themes_keys = telebot.types.InlineKeyboardMarkup(3)
        themes_keys.add(*[telebot.types.InlineKeyboardButton(text=th.theme, callback_data=th.theme) for th in themes])
        themes_keys.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'))

        bot.send_message(call.message.chat.id, '#################################################\n\nВыберите тему\n\n#################################################', reply_markup=themes_keys)
        User.update_memory(call.message.chat.id, {'current_menu': 'themes'})
    elif user_memory.get('current_menu') == 'themes':
        if call.data == 'back':
            categories = ContentCategory.list()
            start_keys = telebot.types.InlineKeyboardMarkup(3)
            start_keys.add(*[telebot.types.InlineKeyboardButton(text=c.category, callback_data=c.category) for c in categories])
            User.update_memory(call.message.chat.id, {'selected_category': '', 'current_menu': 'categories'})

            bot.send_message(call.message.chat.id, '#################################################\n\nЧего желаете?\n\n#################################################', reply_markup=start_keys)
        else:
            content = Content.get_random_content(call.data, call.message.chat.id)
            themes = Themes.list(user_memory.get('selected_category'))
            themes_keys = telebot.types.InlineKeyboardMarkup(3)
            themes_keys.add(*[telebot.types.InlineKeyboardButton(text=th.theme, callback_data=th.theme) for th in themes])
            themes_keys.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'))
            bot.send_message(call.message.chat.id, '*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n%s\n\n%s\n\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*' % (content.title, content.body), reply_markup=themes_keys)


if __name__ == "__main__":
    bot.polling()