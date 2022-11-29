import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import urls

s = requests.session()
vk = vk_api.VkApi(token=urls.urls['token'])
longpoll = VkLongPoll(vk)

list_of_products = {}

places = ["кинотеатр \'русь\'", 'школа №9']
keyboard_for_place = VkKeyboard(one_time=True)
keyboard_for_place.add_button("Кинотеатр \'РУСЬ\'", VkKeyboardColor.PRIMARY)
keyboard_for_place.add_button('Школа №9', VkKeyboardColor.PRIMARY)
times = {'1': '15:00','2': '15:30','3': '16:00','4': '16:30','5': '17:00','6': '17:30',
         '7': '18:00','8': '18:30','9': '19:00','10': '19:30','11': '20:00','12': '20:30','13': '21:00'}


def file_check(user_id, attr=None):
    if not attr:
        try:
            f = open('orders/' + str(user_id) + '.txt', 'r')
            f.close()
            return True
        finally:
            pass
    else:
        try:
            f = open('orders/' + str(user_id) + '.txt', 'r')
            if attr == 1 and 'product' in f.read():
                f.close()
                return True
            elif attr == 2 and 'place' in f.read():
                f.close()
                return True
        except:
            return False


def write_msg(user_id, message, keyboard=None):
    content = {
        'user_id': user_id,
        'message': message,
        'random_id': 0
    }

    if keyboard:
        content['keyboard'] = keyboard.get_keyboard()

    vk.method('messages.send', content)


def listening():
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:

                request = event.text.lower()
                if event.user_id == ********:
                    if request[0:6] == 'accept':
                        msg = ''
                        for line in open('orders/' + request[7:] + '.txt', 'r'):
                            if line[0] != 'u':
                                msg += line
                        write_msg(request[7:], 'Заказ принят\n' + msg)
                else:
                    if request == "начать" or request == 'товары':
                        file = open('orders/' + str(event.user_id) + '.txt', 'w+')
                        r = requests.get(urls.urls['url'], timeout=20)
                        response = json.loads(r.text).get('response')
                        items = response.get('items')
                        message = 'Привет! Вот все доступные товары: \n\n'
                        for i in range(len(items)):
                            name = items[i].get('description')
                            list_of_products[str(i + 1)] = name
                            price = items[i].get('price').get('amount')
                            price = int(price) / 100
                            message += str(i + 1) + ') ' + name + ' ' + str(price) + '₽' + '\n'
                        message += '\nОтправь мне цифру товара, который тебя заинтересовал'
                        write_msg(event.user_id, message)
                        file.close()
                        r.close()

                    elif request in times.keys() and file_check(event.user_id, 2):
                        file = open('orders/' + str(event.user_id) + '.txt', 'a+')
                        print(file.read())
                        write_msg(event.user_id, 'Заказ отправлен на рассмотрение')
                        file.write('time: ' + times.get(request) + '\n')
                        file.write('user_id:' + str(event.user_id))
                        file.seek(0)
                        keyboard_for_response = VkKeyboard(inline=True)
                        keyboard_for_response.add_button('accept ' + str(event.user_id), VkKeyboardColor.POSITIVE)
                        keyboard_for_response.add_button('decline ' + str(event.user_id), VkKeyboardColor.NEGATIVE)
                        write_msg('*********', file.read(), keyboard_for_response)
                        file.close()

                    elif request in places and file_check(event.user_id, 1):
                        msg = ''
                        file = open('orders/' + str(event.user_id) + '.txt', 'a')
                        for f in times.items():
                            msg += f[0] + ') ' + f[1] + '\n'
                        write_msg(event.user_id, 'Введи время встречи от 15:00 до 21:00\n' + msg)
                        file.write('place: ' + request + '\n')
                        file.close()

                    elif request in list_of_products.keys() and file_check(event.user_id):
                        file = open('orders/' + str(event.user_id) + '.txt', 'a')
                        product = list_of_products.get(request)
                        write_msg(event.user_id, 'Введи место встречи', keyboard_for_place)
                        file.write('product: ' + list_of_products.get(request) + '\n')
                        file.close()

                    else:
                        write_msg(event.user_id, 'Введи "Товары", чтобы получить их список')
