from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
import requests
import json

#API c CoinGecko
api_key = 'CG-RrPTA3sYGssjggkKNg4kpJtn'

def get_crypto_data(crypto):
    try:
        response = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={crypto}&api_key={api_key}')
        response.raise_for_status()
        data = response.json()[0]
        return data
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong", err)

def get_top_cryptos():
    try:
        response = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false&api_key={api_key}')
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong", err)

def get_dex_pools(query, network, include, page=1):
    headers = {"x-cg-pro-api-key": api_key}
    try:
        response = requests.get(f'https://pro-api.coingecko.com/api/v3/onchain/search/pools?query={query}&network={network}&include={include}&page={page}', headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Something went wrong",err)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = ('Привет! Я крипто бот от сообщества @CryptoF4m. Я могу предоставить информацию о любой криптовалюте! Напиши /data <crypto-name> для начала работы.')
    await update.message.reply_text(welcome_message)

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto = update.message.text.split()[1]
    data = get_crypto_data(crypto)
    if data:
        await update.message.reply_text(f'Текущая цена {crypto} ${data["current_price"]}. Изменение цены за 24 часа {data["price_change_percentage_24h"]}%.\nРыночная капитализация ${data["market_cap"]}.\nОбщий объем за 24 часа ${data["total_volume"]}.')
    else:
        await update.message.reply_text(f'Извини,я не смог получить данные для {crypto}. Пожалуйста,посмотри название криптовалюты и попробуй снова!')

async def high_low(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto = update.message.text.split()[1]  # get the crypto name from the message
    data = get_crypto_data(crypto)
    if data:
        await update.message.reply_text(f'Самая высокая цена за последние 24 часа для {crypto} ${data["high_24h"]}, и самая низкая цена ${data["low_24h"]}.')
    else:
        await update.message.reply_text(f'Извини,я не смог получить данные для {crypto}. Пожалуйста,посмотри название криптовалюты и попробуй снова!')

# Telegram command to get the circulating supply and total supply of a cryptocurrency
async def supply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto = update.message.text.split()[1]  # get the crypto name from the message
    data = get_crypto_data(crypto)
    if data:
        await update.message.reply_text(f'Циркулирующий запас {crypto} {data["circulating_supply"]}, и общий объем торгов составляет {data["total_supply"]}.')
    else:
        await update.message.reply_text(f'Извини,я не смог получить данные для {crypto}. Пожалуйста,посмотри название криптовалюты и попробуй снова!')

# Telegram command to get the top 10 cryptocurrencies
async def ranks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = get_top_cryptos()
    if data:
        message = "Вот топ-10 криптовалют:\n"
        for i, crypto in enumerate(data, start=1):
            message += f'{i}. *{crypto["name"]}* ({crypto["symbol"].upper()}):\n- Текущая цена ${crypto["current_price"]}\n- Рыночная капитализация ${crypto["market_cap"]}\n- Общий объем за последние 24 часа ${crypto["total_volume"]}\n\n'
            await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text('Извините, мне не удалось получить данные по топ-10 криптовалютам. Пожалуйста, повторите попытку позже.')

# Telegram command to get the on-chain DEX pool data
async def search_pools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    params = update.message.text.split()[1:]  # get the parameters from the message
    query = params[0] if len(params) > 0 else 'weth'
    network = params[1] if len(params) > 1 else 'eth'
    include = params[2] if len(params) > 2 else 'dex'
    page = int(params[3]) if len(params) > 3 else 1
    data = get_dex_pools(query, network, include, page)
    if data and "data" in data:
        message = f"Вот данные пула DEX для запроса {query} в сети {network}:\n"
        for i, pool in enumerate(data["data"], start=1):
            message += f'\n{i}. Pool ID: *{pool["id"]}*\n- Pool Name: {pool["attributes"]["name"]}\n- Base Token Price (USD): ${pool["attributes"]["base_token_price_usd"]}\n- Quote Token Price (USD): ${pool["attributes"]["quote_token_price_usd"]}\n- Base Token Price (Quote Token): {pool["attributes"]["base_token_price_quote_token"]}\n- Quote Token Price (Base Token): {pool["attributes"]["quote_token_price_base_token"]}\n- Total Liquidity: ${pool["attributes"]["reserve_in_usd"]}\n- Price Change Percentage in the last 5 minutes: {pool["attributes"]["price_change_percentage"]["m5"]}%\n- Price Change Percentage in the last 1 hour: {pool["attributes"]["price_change_percentage"]["h1"]}%\n- Price Change Percentage in the last 6 hours: {pool["attributes"]["price_change_percentage"]["h6"]}%\n- Price Change Percentage in the last 24 hours: {pool["attributes"]["price_change_percentage"]["h24"]}%\n'
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096], parse_mode='Markdown')
    else:
        await update.message.reply_text(f'Извините, я не смог получить данные для запроса {query} в сети {network}. Пожалуйста, проверьте запрос и сеть и повторите попытку.')

app = ApplicationBuilder().token('7544904284:AAFWIgtm6UiNk2nD8cCqJjrzUsZSKnaap3E').build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("data", data))
app.add_handler(CommandHandler("high_low", high_low))
app.add_handler(CommandHandler("supply", supply))
app.add_handler(CommandHandler("ranks", ranks))
app.add_handler(CommandHandler("search_pools", search_pools))

app.run_polling()