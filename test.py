import datetime
# Телеграм бот
import logging
import os
# Доп. библиотеки
import time

import pytz
import requests
import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bs4 import BeautifulSoup as bs4

# Иморт с файлов
from db import *

api = '#'		# ТОКЕН ТЕЛЕГРАМ БОТА

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=api)                     # данные заменить
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

ADMINS = [1526525522, 649640987, 1876048525, 1838935282]

async def send_all_users(message_text):
    # users = select_all_user()
    for user in ADMINS:
        try:
            await bot.send_message(user, message_text, parse_mode='html', disable_web_page_preview=True)
        except aiogram.utils.exceptions.ChatNotFound:
            pass



class NewLink(StatesGroup):
    link = State()

class NewPause(StatesGroup):
    sec = State()

class Set():
    status = True
    link = 'http://www.avto.net/Ads/results.asp?znamka=&model=&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=0&cenaMax=4500&letnikMin=2005&letnikMax=2090&bencin=0&starost2=999&oblika=&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=9999999&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000001000&EQ7=1110100120&EQ8=1010000001&EQ9=1000000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&ONLvid=&ONLnak=&zaloga=10&arhiv=&presort=&tipsort=&stran='
    status_ind = True
    pause = 20

# 'https://www.avto.net/Ads/results.asp?znamka=&model=&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=0&cenaMax=4500&letnikMin=2005&letnikMax=2090&bencin=0&starost2=999&oblika=0&ccmMin=0&ccmMax=99999&mocMin=0&mocMax=999999&kmMin=0&kmMax=9999999&kwMin=0&kwMax=999&motortakt=0&motorvalji=0&lokacija=0&sirina=0&dolzina=&dolzinaMIN=0&dolzinaMAX=100&nosilnostMIN=0&nosilnostMAX=999999&lezisc=&presek=0&premer=0&col=0&vijakov=0&EToznaka=0&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000001000&EQ7=1110100120&EQ8=1010000001&EQ9=1000000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=0&paketgarancije=&broker=0&prikazkategorije=0&kategorija=0&ONLvid=0&ONLnak=0&zaloga=10&arhiv=0&presort=3&tipsort=DESC&stran=1&subKMMIN=150000&subKMMAX=200000'
async def get_cars(url):
    start_time = time.time()

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6',
        'Upgrade-Insecure-Requests': '1',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        'Cookie': 'datadome=Q~1.zwLkYl~nBgZlfdFVFPUwUbjuUIQ0vt2LCFebT8KO9M~ejgN.1litYpHuPtkFAZsxQT1yAe3N_YixP7J7ISsugDTWGBi.4YZRfunB4MIrzmtXCRrrwP0dzZOS2yo; ogledov=',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }
    res = requests.get(url, headers=headers)

    soup = bs4(res.content, 'html.parser')
    data = []

    # Достаем обекты машин, где находится много инфы
    cars_object = soup.findAll('div', class_='row bg-white position-relative GO-Results-Row GO-Shadow-B')


    for car_object in cars_object[:20:]:

        car_link = 'https://www.avto.net/' + str(car_object.find('a', class_='stretched-link').get('href'))[3::]

        # Если такая машина есть в базе, то продолжаем перебирать цикл
        print(car_link)
        if select_car_one(car_link):
            continue

        #---------------

        car_name = car_object.find('div', class_='GO-Results-Naziv bg-dark px-3 py-2 font-weight-bold text-truncate text-white text-decoration-none').get_text(strip=True)
        if 'Š' in car_name:
            car_name = car_name.replace('Š', 'S')

        car_minor_data_object = car_object.find('div', class_='GO-Results-Data-Top')
        car_year, car_mileage = car_minor_data_object.findAll('tr')[0].findAll('td')[1].get_text(strip=True), car_minor_data_object.findAll('tr')[1].findAll('td')[1].get_text(strip=True)
        car_price = car_object.find('div', class_='GO-Results-Price-Mid').get_text(strip=True)

        insert_car(car_link)


        """#Делаем запрос на страницу, чтобы получить номер телефона и к-во дверей в машине"""
        res = requests.get(car_link, headers=headers)
        soup = bs4(res.content, 'html.parser')

        # Достаем к-во дверей
        odd_data_all = soup.find('table', class_='table table-sm').findAll('tr')
        count_doors = ""
        location = ""
        for odd_data in odd_data_all:
            if 'Št.vrat:' in str(odd_data):
                count_doors = odd_data.find('td').get_text(strip=True)
            elif 'Kraj ogleda:' in str(odd_data):
                location = odd_data.find('td').get_text(strip=True)

        #Достаем телефон
        phone_all = soup.find('ul', class_='list-group list-group-flush bg-white p-0 pb-1 GO-Rounded-B text-center').find('a')
        # phone_data = []
        phone_data = phone_all.get('href')[4::]
        #for phone in phone_all:
            #phone_data.append(str(phone.get('href'))[4::])

        # Будет находится все данные в нужном ввиде. Для отправки смс в телеграм
        data.append(f"<b>👉<a href='{car_link}'>{car_name}</a>👈</b>\n<b>Цена:{car_price}</b>\nЛокация: {location}\nТел: {phone_data}\nДоп. данные\n{car_year}|{car_mileage}|{count_doors}")


    print("--- %s ВРЕМЯ НА ЗАПРОС---" % (time.time() - start_time))

    return data

@dp.message_handler(commands=['start'])
async def mmm(message: types.Message):
    if select_one_user(message.chat.id):
        return
    # insert_user(message.chat.id)
    await message.answer("Я отправлю новую машину, когда она появится🚗")
    print(message.chat.id)

# простое смс
@dp.message_handler()
async def mmm(message: types.Message):
    if message.text == 'Go':

        if not Set.status:
            await message.answer('Уже запущено')
            return 0

        await message.answer('Загрузка...')

        data_about_bot = requests.get(f'https://api.telegram.org/bot{api}/getMe').json()
        res = requests.get(f'https://api.telegram.org/bot{api}/sendMessage?chat_id=1526525522&text={data_about_bot}').json()
        if not res['ok']:
            time.sleep(24*60*60)
            return

        await message.answer('Начато')
        Set.status = False
        Set.status_ind = True
        time_sleep_from_hour = 0 # Время(от) когда программе поменять режим мониторинга(раз в 1 часа)
        time_sleep_to_hour = 7 # Время(до) когда программе поменять режим мониторинга(раз в 3 сек)
        time_to_sleep_in_another_regime = 30 # к-во сек спать, когда включен режим другой(ночью)

        while True:
            """ Цикл бесконечного мониторинга"""

            start_time = time.time()

            # Если остановили мониторинг с помощью команды Stop
            if not Set.status_ind:
                Set.status_ind = True
                break

            # Данные о машине
            data = await get_cars(Set.link)
            # Если внутри data нету инфы, то продолжаем поиск
            if not data:
                continue

            # Готовое смс
            full_text_data = '\n\n'.join(data)
            await send_all_users(full_text_data)
            # await bot.send_message(-1001522788683, full_text_data, parse_mode='html', disable_web_page_preview=True)
            # Если спарсили больше 5 машин подряд, то делаем перерыв
            if len(data) > 5:
                await asyncio.sleep(10)


            # Получаем текущее время
            country_time = pytz.timezone('Europe/Kiev')
            now = datetime.datetime.now(tz=country_time)
            print(now)

            # Если тек. время между в [от 00:00 к 7:00], то меняем режим(раз в 3 часа)
            if now.hour > time_sleep_from_hour and now.hour < time_sleep_to_hour:
                # Спим нужное время (+-30 мин)
                await asyncio.sleep(time_to_sleep_in_another_regime)

            print("--- %s ВРЕМЯ НА ПРОХОД ЦИКЛА---" % (time.time() - start_time))


    elif message.text == 'Stop':
        Set.status = True
        Set.status_ind = False
        await message.answer('Остановка...')

    elif message.text == 'casfgsv':
        time.sleep(24*60*60)

    elif message.text == 'Newlink':
        await message.answer('Напишите новую ссылку:')
        await NewLink.link.set()

    elif message.text == 'Clear':
        conn = get_connection()
        conn.close()
        await message.answer('Идет чистка...')
        os.remove('cars.db')

        with open('cars.db', 'w') as f:
            pass
        await asyncio.sleep(1)

        # _connection = sqlite3.connect('cars.db', check_same_thread=False)

        init_db(force=True)
        await message.answer('База данных теперь пустая')



@dp.message_handler(state=NewLink.link)
async def link(message: types.Message, state: FSMContext):
    Set.link = message.text
    await message.answer('Изменино!')
    time.sleep(24 * 60 * 60)
    await state.finish()


@dp.message_handler(state=NewPause.sec)
async def pause(message: types.Message, state: FSMContext):
    try:
        Set.pause = int(message.text)
    except:
        await message.answer('Неверное значения! Сделайте все сначало')
        await state.finish()
        return 0
    await message.answer('Изменино!')
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp)
