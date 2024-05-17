import json

import telebot

with open('config.json') as file:
    data = json.load(file)
TOCKEN = data['TOCKEN']

# session = AiohttpSession(proxy='http://proxy.server:3128')
papa_chat = 2109964431


class TelegramPost:
    TOKEN = TOCKEN
    GROUP_ID = papa_chat
    bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

    def send_text(self, text):
        self.bot.send_message(self.GROUP_ID, text=text)


def send_info(text):
    bot = TelegramPost()
    bot.send_text(text=text)


if __name__ == '__main__':
    send_info('''данные о пользователе:
+7 (953) 746 7510
ryazan62nik@yandex.ru
Kola_Zhal

данные о заказе:
Адрес:Novosyolov d50 k2
Время к которому доставить:2024-05-24 11:20:00
Комментарий:await session.close()await session.close()await session.close()

Товары:

Товар:big balloon green
Количество:3

Товар:<little flower red
Количество:2

Товар:hello red
Количество:3''')
