from bot.messages.bookmark import create_saved_bookmark_message
from telegram.ext import (
    ContextTypes,
)
from telegram import Update
from bot.repository import(
    user as user,
    bookmark as bookmark,
)
import logging
import boto3
START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')
bookmark_table = ddb_resource.Table('Bookmark')

def save(
    location_name: str,
    location_coords: str,
    location_addr_ref: str,
    user_id: int,
):
    user.update_save_button(user_id, user_table)    
    try:
        response = bookmark.create_bookmark({
            "location_name": location_name,
            "location_coords": location_coords,
            "location_addr_ref": location_addr_ref,
            "user_id": user_id,
        }, bookmark_table)
        return response
    except Exception as e:
        logging.error("Error saving data", e)
        return None


async def save_to_bookmarks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    print("hixcxc")
    
    location_name = context.user_data["loc1"]+"|||"+context.user_data["loc2"]
    location_coords = context.user_data["loc1_lat"]+","+context.user_data["loc1_lng"]+";"+context.user_data["loc2_lat"]+","+context.user_data["loc2_lng"]
    location_addr_ref = context.user_data["loc1_addr_ref"]+";"+context.user_data["loc2_addr_ref"]
    user_id = context.user_data["id"]

    if not context.user_data["loc1"] or not context.user_data["loc2"]:
        await query.message.reply_text(text="No location found")
        return
    print("hisz")

    success = save(
        location_name,
        location_coords,
        location_addr_ref,
        user_id,
    )
    print("hixczc")

    await query.answer()
    print("h", success)

    if success["success"] is True:
        await query.message.reply_text(create_saved_bookmark_message())
    elif success["message"] == "Bookmark already exists":
        await query.message.reply_text("Hello, bookmark already exists leh!!")
    return START_ROUTES
