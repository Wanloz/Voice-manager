import os
from dotenv import load_dotenv

load_dotenv()
VA_NAME = 'Bot'
VA_ALIAS = ('americano')
VA_TBR = ('скажи', 'покажи', 'ответь', 'произнеси', 'расскажи', 'сколько', 'слушай')

# -1 это стандартное записывающее устройство
MICROPHONE_INDEX = -1

# Путь к браузеру Google Chrome
CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'

# Токен Picovoice
PICOVOICE_TOKEN = os.getenv('PICOVOICE_TOKEN')

# Токен OpenAI
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')



