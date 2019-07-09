import telebot
from telebot import types
from telebot.types import Message
import config
import keys
import shelve
import pyqiwi
import re
from deuslib import Mongo, Data

qiwidb =    shelve.open("qiwi", flag="c", protocol=None, writeback=False) # хранлище номер-токен
mg =        Mongo().mg() # если понадобится что-то с монгой
bot =       telebot.TeleBot(config.token)

@bot.message_handler(commands=[ 'start' ])
def startcom(message: Message):
    bot.send_message(message.chat.id, "Приветствую. Ты находишься в менеджере интернет-кошельков, выбери платёжку.", reply_markup=keys.mainkb)

@bot.message_handler(commands=[ 'qiwi' ])
def qiwicom(message: Message):
    amount =    Data().get_many('qiwi', 'qiwi', key='owner', value=message.chat.id)
    if amount:
        bot.send_message(message.chat.id, "QiwiManager activated\n\nВсего кошельков - {}".format(str(len(list(amount)))), reply_markup=keys.qiwik)
    else:
        bot.send_message(message.chat.id, "QiwiManager activated", reply_markup=keys.qiwik)

@bot.callback_query_handler(func=lambda c: c.data == 'qiwisend')
def ev(callback_query: types.CallbackQuery):
    global c_message
    c_message =     callback_query.message
    message_id =    callback_query.message.message_id

    msg =           bot.send_message(c_message.chat.id, "Введите номер получателя: ", reply_markup=keys.backkb)
    bot.register_next_step_handler(msg, sendcom)

def sendcom(number: Message):
    global num
    num =       number.text

    if num == "Отмена":
        msg =       bot.send_message(number.chat.id, "Отменено", reply_markup=keys.qiwik)
        bot.edit_message_reply_markup(number.chat.id, msg.message_id)
    else:
        msg =   bot.send_message(number.chat.id, "Введите сумму: ")
        bot.register_next_step_handler(msg, amountcom)

def amountcom(amount: Message):
    global sum
    sum =               amount.text

    for a in qiwidb.keys():
        if a in c_message.text:
            wallet =    pyqiwi.Wallet(token=qiwidb[str(a)], number=a)
            pay =       wallet.send('99', str(num), float(sum), comment='mMm')
            print(pay)
            print(pay.transaction)
            print(pay.transaction.state)
            info =      'Статус {0}\nПолучатель: {1}\nСумма перевода: {2}'.format(pay.transaction.state, pay.fields.account, pay.sum.amount)

            bot.send_message(amount.chat.id, info)

@bot.callback_query_handler(func=lambda c: c.data == 'display_all')
def ev(callback_query: types.CallbackQuery):
    message =       callback_query.message
    message_id =    callback_query.message.message_id

    for a in list(qiwidb.items()):
        wallet =    pyqiwi.Wallet(token=a[1], number=a[0])

        def balance():
            for b in wallet.accounts:
                return b.balance.get('amount')

        text =      "Номер - /{}\nТокен - {}\nБаланс - {}".format(wallet.number, wallet.token, balance())
        bot.send_message(message.chat.id, text)

@bot.callback_query_handler(func=lambda c: c.data == 'qiwiadd')
def ev(callback_query: types.CallbackQuery):
    message =       callback_query.message
    message_id =    callback_query.message.message_id

    msg =           bot.send_message(message.chat.id, "Введите номер вместе с +", reply_markup=keys.backkb)
    bot.register_next_step_handler(msg, qiwiadd)

def qiwiadd(number: Message):
    global num
    num =       number.text

    if number.text == "Отмена":
        msg =       bot.send_message(number.chat.id, "Отменено", reply_markup=keys.qiwik)
        bot.edit_message_reply_markup(number.chat.id, msg.message_id)
    else:
        msg =       bot.send_message(number.chat.id, "Введите токен")
        bot.register_next_step_handler(msg, tokenadd)

def tokenadd(tok: Message):
    global qiwit
    qiwit =             tok.text

    try:
        if str(num) in qiwidb:
            bot.send_message(tok.chat.id, "Такой аккаунт уже есть")
        else:
            wallet =    pyqiwi.Wallet(token=qiwit, number=num)

            def balance():
                for b in wallet.accounts:
                    return b.balance.get('amount')

            qiwidb[str(num[1:])] =  str(qiwit)
            json =      {
                        "number": num[1:],
                        "token": qiwit,
                        "balance": balance(),
                        "owner": tok.chat.id,
                        }

            Data().add("qiwi", "qiwi", json=json)
            bot.send_message(tok.chat.id, "Добавлено успешно.", reply_markup=keys.qiwik)

    except Exception as e:
        print(e)
        bot.send_message(tok.chat.id, "Что-то введено не верно.")

    qiwidb.sync()

@bot.message_handler(func=lambda c: c.text[1:] in list(qiwidb.keys()))
def numcom(message: Message):
    number =        Data().get('qiwi', 'qiwi', key='number', value=str(message.text[1:]))

    if message.chat.id == number['owner']:
        wallet =    pyqiwi.Wallet(token=qiwidb[str(message.text[1:])], number=message.text[1:])

        def balance():
            for b in wallet.accounts:
                return b.balance.get('amount')

        text =      "Номер - /{}\nТокен - {}\nБаланс - {}".format(message.text[1:], qiwidb[str(message.text[1:])], balance())
        bot.send_message(message.chat.id, text, reply_markup=keys.qiwiak)

    else:
        bot.send_message(message.chat.id, "Номер не зарегистрирован на вас")

@bot.message_handler(content_types=[ 'text' ])
def textcom(message: Message):
    bot.send_message(message.chat.id, "???", reply_markup=keys.mainkb)


bot.polling(interval=0, none_stop=True)