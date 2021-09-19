import requests
from bs4 import BeautifulSoup as bs4


# Телеграм бот
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.callback_query import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# Доп. библиотеки
import time
import asyncio
import os
import datetime
import pytz

# Иморт с файлов
from db import *
import shutil

import requests

api = '2032151564:AAHYo7Dmpa801Pu3MNlTCLHG1xfTm_VT5Lo'		# ТОКЕН ТЕЛЕГРАМ БОТА

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=api)                     # данные заменить
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

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
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }
    res = requests.get(url, headers=headers)

    soup = bs4(res.content, 'html.parser')

    # Достаем обекты машин, где находится много инфы
    car_object = soup.find('div', class_='row bg-white position-relative GO-Results-Row GO-Shadow-B')
    car_link = 'https://www.avto.net/' + str(car_object.find('a', class_='stretched-link').get('href'))[3::]

    print("--- %s ВРЕМЯ НА ЗАПРОС---" % (time.time() - start_time))

    # Если такая машина есть в базе, то продолжаем перебирать цикл
    print(car_link)
    if select_car_one(car_link):
        return False

    #---------------

    car_name = car_object.find('div', class_='GO-Results-Naziv bg-dark px-3 py-2 font-weight-bold text-truncate text-white text-decoration-none').get_text(strip=True)
    if 'Š' in car_name:
        car_name = car_name.replace('Š', 'S')

    car_minor_data_object = car_object.find('div', class_='GO-Results-Data-Top')
    car_year, car_mileage = car_minor_data_object.findAll('tr')[0].findAll('td')[1].get_text(strip=True), car_minor_data_object.findAll('tr')[1].findAll('td')[1].get_text(strip=True)
    car_price = car_object.find('div', class_='GO-Results-Price-Mid').get_text(strip=True)

    insert_car(car_link)

    # Будет находится все данные в нужном ввиде. Для отправки смс в телеграм
    data = f"<b>{car_name}</b>\nСсылка: {car_link}\n<b>Цена:{car_price}</b>\nДоп. данные\n{car_year}|{car_mileage}"

    print(data)
    return data

@dp.message_handler(commands=['start'])
async def mmm(message: types.Message):
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
        try:
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
                full_text_data = data
                await bot.send_message(-1001522788683, full_text_data, parse_mode='html', disable_web_page_preview=True)


                # Получаем текущее время
                country_time = pytz.timezone('Europe/Kiev')
                now = datetime.datetime.now(tz=country_time)
                print(now)

                # Если тек. время между в [от 00:00 к 7:00], то меняем режим(раз в 3 часа)
                if now.hour > time_sleep_from_hour and now.hour < time_sleep_to_hour:
                    # Спим нужное время (+-30 мин)
                    await asyncio.sleep(time_to_sleep_in_another_regime)

                print("--- %s ВРЕМЯ НА ПРОХОД ЦИКЛА---" % (time.time() - start_time))

        except Exception as e:
            print(e)
            await bot.send_message(1526525522, 'I have fallen. (cars)')

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
