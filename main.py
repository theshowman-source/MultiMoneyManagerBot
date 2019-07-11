import telebot
from telebot        import types
from telebot.types  import Message
import config
import keys
import shelve
import pyqiwi
from deuslib        import Mongo, Data
import cherrypy

qiwidb =    shelve.open("qiwi", flag="c", protocol=None, writeback=False) # хранлище номер-токен
mg =        Mongo().mg() # если понадобится что-то с монгой
bot =       telebot.TeleBot(config.token)


WEBHOOK_HOST = '0.0.0.0'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

for i in mg.qiwi.qiwi.find():
    qiwidb[str(i['number'])] = str(i['token'])

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

@bot.callback_query_handler(func=lambda c: c.data == 'qiwidel')
def ev(callback_query: types.CallbackQuery):
    global message
    message =       callback_query.message
    message_id =    callback_query.message.message_id

    msg = bot.send_message(message.chat.id, "Вы уверены что хотите удалить номер?", reply_markup=keys.surekb)
    bot.register_next_step_handler(msg, suredelete)

def suredelete(sure_m: Message):
    global choice
    choice = sure_m.text

    if choice == "Уверен":
        for a in qiwidb.keys():
            if a in message.text:
                del qiwidb[str(a)]
                Data().remove('qiwi', 'qiwi', key='number', value=a)

    else:
        bot.send_message(sure_m, "Отменено")

@bot.callback_query_handler(func=lambda c: c.data == 'qiwiedit')
def ev(callback_query: types.CallbackQuery):
    global message
    message =       callback_query.message
    message_id =    callback_query.message.message_id

    msg =           bot.send_message(message.chat.id, "Введите новый токен")
    bot.register_next_step_handler(msg, newtoken)

def newtoken(nt_msg: Message):
    global nt
    nt =            str(nt_msg.text)

    for a in qiwidb.keys():
        if a in message:
            num =   Data().get('qiwi', 'qiwi', key='number', value=a)
            qiwidb[str(a)] = str(nt)
            Data().update('qiwi', 'qiwi', item=num, key='token', value=nt)
            bot.send_message(nt_msg.chat.id, 'Успешно обновлено')

@bot.callback_query_handler(func=lambda c: c.data == 'qiwisend')
def ev(callback_query: types.CallbackQuery):
    global c_message
    c_message =     callback_query.message
    message_id =    callback_query.message.message_id

    msg =           bot.send_message(c_message.chat.id, "Введите номер получателя (без +): ", reply_markup=keys.backkb)
    bot.register_next_step_handler(msg, sendcom)

def sendcom(number: Message):
    global num
    num =               number.text

    if num ==           "Отмена":
        msg =           bot.send_message(number.chat.id, "Отменено", reply_markup=keys.qiwik)
        bot.edit_message_reply_markup(number.chat.id, msg.message_id)
    else:
        try:
            check =         int(num)
            check -=        1
            msg =           bot.send_message(number.chat.id, "Введите сумму (только число): ")
            bot.register_next_step_handler(msg, amountcom)
        except:
            bot.send_message(number.chat.id, "Что-то не так, попробуйте убрать все буквы")

def amountcom(amount: Message):
    global sum
    sum =           amount.text
    try:
        check =     float(sum)
        check -=    1
        msg =       bot.send_message(amount.chat.id, "Хотите добавить комментарий к платежу?", reply_markup=keys.surekb)
        bot.register_next_step_handler(msg, comcom)
    except:
        bot.send_message(amount.chat.id, "Что-то не так, попробуйте убрать все буквы")

def comcom(comment: Message):
    global com
    com =                   comment.text

    if com ==               "Да":
        msg = bot.send_message(comment.chat.id, "Введите комментарий: ", reply_markup=keys.backkb)
        bot.register_next_step_handler(msg, comtext)
    elif com ==             "Отмена":
        bot.send_message(comment.chat.id, "Отменено")
    else:
        msg2 =              bot.send_message(comment.chat.id, "Получатель: {}\nСумма: {}\n\nОтправляем?".format(num, sum), reply_markup=keys.surekb)
        bot.register_next_step_handler(msg2, confirm)

def confirm(conf: Message):
    if conf.text ==         "Да":
        for a in qiwidb.keys():
            if a in c_message.text:
                wallet =    pyqiwi.Wallet(token=qiwidb[str(a)], number=a)
                pay =       wallet.send('99', str(num), float(sum))
                info =      'Статус {0}\nПолучатель: {1}\nСумма перевода: {2}'.format(pay.transaction.state,pay.fields.account, pay.sum.amount)

                bot.send_message(conf.chat.id, info)
    else:
        bot.send_message(conf.chat.id, "Отменено")

def comtext(com_text: Message):
    global ct
    ct =                    com_text.text

    if ct ==                "Отмена":
        bot.send_message(com_text.chat.id, "Отменено")
    else:
        for a in qiwidb.keys():
            if a in c_message.text:
                wallet =    pyqiwi.Wallet(token=qiwidb[str(a)], number=a)
                pay =       wallet.send('99', str(num), float(sum), comment=str(ct))
                info =      'Статус {0}\nПолучатель: {1}\nСумма перевода: {2}'.format(pay.transaction.state,pay.fields.account, pay.sum.amount)

                bot.send_message(com_text.chat.id, info)

@bot.callback_query_handler(func=lambda c: c.data == 'display_all')
def ev(callback_query: types.CallbackQuery):
    message =       callback_query.message
    message_id =    callback_query.message.message_id

    all =           Data().get_many('qiwi', 'qiwi', key='owner', value=message.chat.id)

    for a in all:
        wallet =    pyqiwi.Wallet(token=a['token'], number=a['number'])

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


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

bot.remove_webhook()

 # Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

#bot.polling(interval=0, none_stop=True)