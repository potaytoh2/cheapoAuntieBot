from telegram.ext import (
    ContextTypes,
)
from telegram import Update, ReplyKeyboardMarkup
from ..utils.db import insert_user, user_exists
from ..api.price import get_dest_addr_ref
from bot.repository import(
    user as user_db
)
import boto3
START_ROUTES,SELECT_START_LOCATION,SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.lower()  
    user = update.message.from_user
    context.user_data["id"] = user.id
    context.user_data["first_name"] = user.first_name
    context.user_data["username"] = user.username
    user_db.update_add_command(user.id,user_table)
    if not user_db.user_exists(user.id):
        user_db.create_user({"user_id": user.id, "name": user.name, "username": user.username}, user_table)

    locations_input=user_input[len("/add"):].strip()
    locations = locations_input.split(" to ")

    if len(locations) != 2:
        response = "Please enter two locations in the format: \r\n\r\n/add <location1> to <location2>"
        await update.message.reply_text(response)
        return

    location1 = locations[0].strip()
    location2 = locations[1].strip()
    context.user_data["location1"] = location1
    context.user_data["location2"] = location2
    context.user_data["isAdd"]=True
    try:
        location1Data=get_dest_addr_ref(location1)
        context.user_data["loc1_data"] = location1Data
        print("add function's: location1Data", location1Data)
        reply_keyboard = [[location["name"]] for location in location1Data]
        keyboardMarkup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,resize_keyboard=True)
        context.user_data["location1Data"] = location1Data
    except Exception as e:
        print("An error occured at addd:", e)
        return "An error occurred: {}".format(e)
    
    await update.message.reply_text("Please select the location for starting location", reply_markup=keyboardMarkup)

    return SELECT_START_LOCATION
    