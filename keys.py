import telebot
from telebot import types

qiwik =             types.InlineKeyboardMarkup()
qiwiadd =           types.InlineKeyboardButton(text="Добавить", callback_data='qiwiadd')
qiwiedit =          types.InlineKeyboardButton(text="Изменить", callback_data='qiwiedit')
qiwiall =           types.InlineKeyboardButton(text="Вывести все", callback_data='display_all')
qiwidel =           types.InlineKeyboardButton(text="Удалить", callback_data='qiwidel')
qiwisend =          types.InlineKeyboardButton(text="Отправить", callback_data='qiwisend')

qiwik.add(qiwiadd)
qiwik.add(qiwiall)

qiwiak =            types.InlineKeyboardMarkup()
qiwiak.add(qiwiedit, qiwidel)
qiwiak.add(qiwisend)

mainkb =            types.ReplyKeyboardMarkup(resize_keyboard=True)

qiwib =             types.KeyboardButton(text="/qiwi")

mainkb.add(qiwib)

backkb =            types.ReplyKeyboardMarkup(resize_keyboard=True)
backb =             types.KeyboardButton(text="Отмена")

backkb.add(backb)