import telebot
from telebot import types

qiwiadd =           types.InlineKeyboardButton(text="Добавить", callback_data='qiwiadd')
qiwiedit =          types.InlineKeyboardButton(text="Изменить токен", callback_data='qiwiedit')
qiwiall =           types.InlineKeyboardButton(text="Вывести все", callback_data='display_all')
qiwidel =           types.InlineKeyboardButton(text="Удалить", callback_data='qiwidel')
qiwisend =          types.InlineKeyboardButton(text="Отправить", callback_data='qiwisend')

qiwik =             types.InlineKeyboardMarkup()
qiwik.add(qiwiadd)
qiwik.add(qiwiall)

qiwiak =            types.InlineKeyboardMarkup()
qiwiak.add(qiwiedit, qiwidel)
qiwiak.add(qiwisend)

qiwib =             types.KeyboardButton(text="/qiwi")

mainkb =            types.ReplyKeyboardMarkup(resize_keyboard=True)
mainkb.add(qiwib)

backb =             types.KeyboardButton(text="Отмена")

backkb =            types.ReplyKeyboardMarkup(resize_keyboard=True)
backkb.add(backb)

sureb =             types.KeyboardButton(text="Уверен")
nosureb =           types.KeyboardButton(text="Нет, я передумал")

surekb =            types.ReplyKeyboardMarkup(resize_keyboard=True)
surekb.add(sureb)
surekb.add(nosureb)