from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, InlineKeyboardButton,
    InlineKeyboardMarkup, PhotoSize, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    ConversationHandler, MessageHandler, StringCommandHandler,
    filters, PreCheckoutQueryHandler, CallbackQueryHandler, CallbackContext,
)
import os
from dotenv import load_dotenv
import logging
import requests

load_dotenv() #important!

# Web 3
from web3 import Web3

http_endpoint = os.getenv("HTTP_ENDPOINT_ETH")
web3 = Web3(Web3.HTTPProvider(http_endpoint))


# Web 3 Price Feeds Contract
wss_endpoint = os.getenv("WSS_ENDPOINT_SEPOLIA")
alchemy_node = Web3.WebsocketProvider(wss_endpoint)
node = Web3(alchemy_node)
abi = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [],
      "name": "getLatestPrices",
      "outputs": [
        {
          "internalType": "int256",
          "name": "",
          "type": "int256"
        },
        {
          "internalType": "int256",
          "name": "",
          "type": "int256"
        },
        {
          "internalType": "int256",
          "name": "",
          "type": "int256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getNames",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "pure",
      "type": "function"
    }
  ]

# Loggerdea
logger = logging.getLogger(__name__)

# Telegram
TELE_TOKEN_TEST = os.getenv("TELE_TOKEN")
ROUTE, ADD_WALLET,CHECK_RESPONSE = range(3)

"""
This is where the fun begins
"""
web_link = "https://defilytics.netlify.app/"

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nfts'] = []
    # code below deletes users message to the bot
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    keyboard = [
        [InlineKeyboardButton("Demo Wallet", callback_data="demo_wallet"),],
        [InlineKeyboardButton("Add Wallet", callback_data="add_wallet"),],
        [InlineKeyboardButton("View Prices", callback_data="loading_prices"),],
        # [InlineKeyboardButton("Connect Wallet", web_app={"url":web_link})],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = "Hello Stranger, are you ready to begin your defilytics journey?"

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=message, 
            parse_mode="markdown", 
            reply_markup=reply_markup
        )
    else:
        original_message = await context.bot.send_message( # I want to store this message so that I can delete it later on
            chat_id=update.effective_chat.id, 
            text=message, 
            parse_mode="markdown", 
            reply_markup=reply_markup
        )
        context.user_data['original_message'] = original_message

    return ROUTE

async def loading_prices(update, context: ContextTypes.DEFAULT_TYPE):
    loading_message = "Checking the prices please wait..."
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=loading_message)
    await view_prices(update,context)
    await message.delete()
    return ROUTE

async def view_prices(update, context: ContextTypes.DEFAULT_TYPE):
    cid = "0x6b80929038568680A6f9Acb8017843f7e2E6A739" # PriceFeeds Contract
    bid = node.eth.block_number
    # uid = -1
    contract = node.eth.contract(Web3.to_checksum_address(cid), abi=abi)

    query_prices = f"contract.functions.{'getLatestPrices()'}.call(block_identifier = {bid})"
    prices = eval(query_prices)
    query_names = f"contract.functions.{'getNames()'}.call(block_identifier = {bid})"
    names = eval(query_names)

    message = ""

    for i in range(len(prices)):
        message += f"\n{names[i]} (USD): ${round(prices[i] / 100000000,2)}\n"

    query = update.callback_query
    await query.answer()

    keyboard = [ # may have to remove this inline keyboard a bit buggy
        [InlineKeyboardButton("Back", callback_data="start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        # chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup, 
    )

    return ROUTE

async def demo_wallet(update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = '0x07b89a4c67206c82bd8c1a3944299c1c8f52553e'
    context.user_data['demo'] = True
    await view_wallet(update,context)
    return ROUTE

async def add_wallet(update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['demo'] = False
    query = update.callback_query
    await query.answer()

    # keyboard = [ # may have to remove this inline keyboard a bit buggy
    #     [InlineKeyboardButton("Back", callback_data="start")],
    # ]
    message = "Please enter the wallet address"
    # reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        # chat_id=update.effective_chat.id,
        text=message,
        # reply_markup=reply_markup, 
    )

    return ADD_WALLET
    
#     await check_response_add(update,context)

async def check_response_add(update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()
    if query.data == "start":
        start(update,context)
        print("hello from the wrong side")
        return ROUTE
    else:
        print('hello from the other side')
        return ADD_WALLET
    

async def register_wallet(update, context: ContextTypes.DEFAULT_TYPE):

    # code below deletes the old bot message that is stored in the context
    original_message = context.user_data['original_message'] # initialized during the start function
    await original_message.delete()
    
    wallet = update.message.text
    context.user_data['address'] = wallet
    await view_wallet(update,context)

    # code below deletes users message to the bot
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return ROUTE

async def view_wallet(update, context: ContextTypes.DEFAULT_TYPE):

    address = context.user_data['address']

    print(f"Your address is {address}")

    message = f"Your Wallet Address is {address}"

    # to get NFTs
    api_endpoint = f'https://api.opensea.io/api/v1/assets?owner={address}&order_direction=desc&offset=0&limit=20'

    headers = {
        "accept": "application/json",
        "X-API-KEY": os.getenv("OPENSEA_API")
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        context.user_data['nfts'] = data

    else:
        context.user_data['nfts'] = []

    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("Back", callback_data="start")],
        [InlineKeyboardButton("View Balance", callback_data="view_balance")],
        [InlineKeyboardButton("View NFTs", callback_data="get_nfts")], # 0 to indicate the current position of the nft in the asset list, default is zero since its the first item
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query != None: #or query != None
        await query.answer()
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )
    else:
        original_message = await update.message.reply_text( # similar to start this will act as the original message to be deleted once the previous message the bot sends has been deleted, will start a new chain
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )
        context.user_data['original_message'] = original_message

    return ROUTE

async def view_balance(update, context: ContextTypes.DEFAULT_TYPE):
    
    address = context.user_data['address']

    message = ""

    # Wallet balance
    try:
        address_checksummed = Web3.to_checksum_address(address)
        balance = web3.eth.get_balance(address_checksummed)
        balance_in_ether = balance / 10**18

        message = f"Wallet balance: {round(balance_in_ether,2)} ETH"

    except Exception as e:
        print("An error occured: ",e)
        message = "The wallet added does not seem to have a proper wallet address"

    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Back", callback_data="view_wallet")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        # chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup, 
    )

    return ROUTE

async def get_nfts(update, context: ContextTypes.DEFAULT_TYPE):
    
    address = context.user_data['address']

    # to get NFTs
    api_endpoint = f'https://api.opensea.io/api/v1/assets?owner={address}&order_direction=desc&offset=0&limit=20'

    headers = {
        "accept": "application/json",
        "X-API-KEY": os.getenv("OPENSEA_API")
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        context.user_data['nfts'] = data

    else:
        context.user_data['nfts'] = {}

    print("get nfts is activated")
    await view_nfts(update,context) # Call view_nfts with the updated context "view_nfts_0" (not really, we failed at this, attempt next time)
    return ROUTE

async def view_nfts(update, context: ContextTypes.DEFAULT_TYPE):
    
    nfts = context.user_data['nfts']

    message = ""
    
    query = update.callback_query
    await query.answer()
    page = query.data.split("_")[-1]
    page_num = 0
    if page == "nfts": #first time being called from get nfts
        pass
        # Set the desired callback data as "view_nfts_0"
        # context.args = ["view_nfts_0"] # Important!!! - what could have been, basically trying to achieve this
        # 0 to indicate the current position of the nft in the asset list, default is zero since its the first item
    else:
      page_num = int(page) # getting the 1 if view_nfts_1 which is the page_num or position in the list

    print(page_num)

    try:
        if nfts['assets'] != []:

            nft = nfts['assets'][page_num]

            message += "View your nft below!\n"

            # for asset in nfts['assets']:
            name = nft['name']
            image_url = nft['image_url']
            description = nft['description']

            nft_info = f"\nNFT Name: {name}\n\nDescription: {description}\n\nImage URL: {image_url}"

            print(name)

            # # Create a photo message with a caption
            # context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url, caption=nft_info)

            # # Truncate the message if it exceeds a certain length
            # if len(message + nft_info) <= 4096:
            message += nft_info
            # else:
            #     pass
            
            keyboard = [
                [InlineKeyboardButton("Back to Wallet Page", callback_data="view_wallet")],
            ]

            if page_num > 0:
                keyboard.append([InlineKeyboardButton("Previous", callback_data=f"view_nfts_{page_num-1}")])

            last_index = len(nfts['assets']) - 1

            if page_num < last_index:
                keyboard.append([InlineKeyboardButton("Next", callback_data=f"view_nfts_{page_num+1}")])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                # chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup, 
            )

        else:
            # message += f"/n/nError: {response.status_code} - {response.text}"
            message += "This wallet has no NFTs!"
            keyboard = [
                [InlineKeyboardButton("Back", callback_data="view_wallet")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                # chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup, 
            )

    except Exception as e:
        print("An error occured: ",e)
        message = "The wallet added does not seem to have a proper wallet address"
        keyboard = [
            [InlineKeyboardButton("Back", callback_data="view_wallet")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            # chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup, 
        )

    return ROUTE

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry did not understand that command please use /start" 
    )
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN_TEST).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        fallbacks=[MessageHandler(filters.TEXT, unknown)],
        states = {
            ROUTE: {                
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(demo_wallet, pattern="^demo_wallet$"),
                CallbackQueryHandler(add_wallet, pattern="^add_wallet$"),
                CallbackQueryHandler(loading_prices, pattern="^loading_prices$"),
                CallbackQueryHandler(view_prices, pattern="^view_prices$"),
                CallbackQueryHandler(view_wallet, pattern="^view_wallet$"),
                CallbackQueryHandler(view_balance, pattern="^view_balance$"),
                CallbackQueryHandler(get_nfts, pattern="^get_nfts$"),
                CallbackQueryHandler(view_nfts, pattern="^view_nfts_(.*)$") # the reason we add the (.*) at the back is because we need to implement some form of pagination, this last "parameter" acts as the page number which is set default to zero in view_wallet function when it calls view_nfts
            },
            ADD_WALLET: [MessageHandler(filters.TEXT,register_wallet)],
            CHECK_RESPONSE: [MessageHandler(filters.TEXT,check_response_add)],})

    application.add_handler(conversation_handler)
    application.run_polling()
    logger.info("Application running via polling")
