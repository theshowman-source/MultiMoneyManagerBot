import pymongo

class Mongo:
    def mg(self):
        mg = pymongo.MongoClient("connect to mongodb here")
        return mg

mg = Mongo().mg()

class Data:
    def add(self, db, collection, json=None, message=None, ref=None):
        if json:
            mg[db][collection].insert_one(json)
            mg.close()
        elif message:
            if not ref:
                ui = {"chat_id": message.chat.id,
                      "balance": float(0),
                      "username": message.from_user.username,
                      "status": "default"}
                mg[db][collection].insert_one(ui)
                mg.close()
            else:
                ui = {"chat_id": message.chat.id,
                      "balance": float(0),
                      "username": message.from_user.username,
                      "status": ref}
                mg[db][collection].insert_one(ui)
                mg.close()

    def get(self, db, collection, key=None, value=None, message=None):
        if message:
            user = mg[db][collection].find_one({"chat_id": message.chat.id})
            mg.close()
            return user
        else:
            user = mg[db][collection].find_one({key: value})
            mg.close()
            return user

    def get_many(self, db, collection, key=None, value=None, message=None, fil=None):
        if message:
            user = mg[db][collection].find({"chat_id": message.chat.id})
            mg.close()
            return user
        elif fil:
            user = mg[db][collection].find(filter=None)
            mg.close()
            return user
        else:
            user = mg[db][collection].find({key: value})
            mg.close()
            return user


    def update(self, db, collection, key, value, user=None):
        mg[db][collection].update_one(user, {"$set": {key: value}})

class Pay:
    def paykey(self, sum, id, qiwi=None, yandex=None, card=None):
        from telebot import types
        pkb = types.InlineKeyboardMarkup()
        global qb, yb, cb
        if qiwi:
            qiwiurl = "https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={0}&amountInteger={1}&amountFraction=0&extra%5B%27comment%27%5D={2}&currency=643".format(qiwi, sum, id)
            qb = types.InlineKeyboardButton(text="QIWI", url=qiwiurl)
            pkb.add(qb)

        if yandex:
            yandexurl = "https://money.yandex.ru/transfer?receiver={0}&sum={1}&successURL=&quickpay-back-url=&shop-host=&label=&targets={2}&comment={2}&origin=form&selectedPaymentType=PC&destination={2}%3B%0A{2}&form-comment={2}&short-dest=&quickpay-form=shop".format(yandex, sum, id)
            yb = types.InlineKeyboardButton(text="YANDEX", url=yandexurl)
            pkb.add(yb)

        if card:
            cardurl = "https://money.yandex.ru/transfer?receiver={0}&sum={1}&successURL=&quickpay-back-url=&shop-host=&label=&targets={2}&comment={2}&origin=form&selectedPaymentType=AC&destination={2}%3B%0A{2}&form-comment={2}&short-dest=&quickpay-form=shop".format(card, sum, id)
            cb = types.InlineKeyboardButton(text="Картой(YANDEX)", url=cardurl)
            pkb.add(cb)

        return pkb

