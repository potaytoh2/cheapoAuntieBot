from bot.api.price import get_gojek_price, get_tada_price, get_zig_price
from bot.messages.price_query import create_loading_message, create_price_query_message
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from ..utils.db import cur
from bot.repository import(
    user as user,
    bookmark as bookmark,
    query as query,
    userTravelHistory as userTravelHistory,
)
from bot.utils.helper import get_epoch_time
import boto3
import asyncio
import re

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')
bookmark_table = ddb_resource.Table('Bookmark')
query_table = ddb_resource.Table('Query')
user_travel_history_table = ddb_resource.Table('UserTravelHistory')
async def fetch_data():
    # Simulating a network request delay
    await asyncio.sleep(1)
    return "New data loaded"


async def handle_numeric_command(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text

    match = re.match(r"^/(\d+)$", message_text)
    if not match:
        pass
    integer_command = int(match.group(1))  # Extract the integer
    user_id = update.message.from_user.id
    user.update_bookmark_call(user_id,user_table)

    entry = bookmark.get_bookmark_by_num_id(user_id, integer_command,bookmark_table)
    print(entry)
    location_separate = entry['location_coords'].split(";")
    location_coords = [coords.split(",") for coords in location_separate]
    loc1_lat,loc1_lng = location_coords[0]
    loc2_lat,loc2_lng = location_coords[1]
    location_addr_ref = entry['location_addr_ref'].split(";")
    loc1_addr_ref = location_addr_ref[0]
    loc2_addr_ref = location_addr_ref[1]

    gojek_price = get_gojek_price(
        float(loc1_lat), float(loc1_lng), float(loc2_lat), float(loc2_lng)
    )
    tada_price = get_tada_price(loc1_lat, loc1_lng, loc2_lat, loc2_lng)
    zig_price = get_zig_price(
        loc1_lat, loc1_lng, int(loc1_addr_ref), loc2_lat, loc2_lng, int(loc2_addr_ref)
    )

    context.user_data["gojek_price"] = gojek_price / 100.0
    context.user_data["tada_price"] = tada_price
    context.user_data["zig_price"] = zig_price
    gojek_price = "{:.2f}".format(gojek_price / 100.0)
    tada_price = "{:.2f}".format((tada_price))

    gojek_price = "{:.2f}".format(float(gojek_price) + 0.3)
    tada_price = "{:.2f}".format(float(tada_price) + 0.1)
    zig_price = "{:.2f}".format(float(zig_price) - 0.1)

    response = create_loading_message()
    keyboard = [
        [
            InlineKeyboardButton(
                "Open in Gojek",
                url="https://proxy-206.vercel.app/?scheme=gojek&path=x/",
            ),
            InlineKeyboardButton(
                "Open in Tada",
                url="https://proxy-206.vercel.app/?scheme=tada&path=x/",
            ),
            InlineKeyboardButton(
                "Open in Zig",
                url="https://proxy-206.vercel.app/?scheme=zig&path=x/",
            ),
        ]
    ]

    message = await update.message.reply_text(response)

    await fetch_data()

    # ERROR HERE PLS FIX
    user.update_check_command(user_id,user_table)
    query.create_query({
        "user_id": user_id,
        'timestamp': get_epoch_time(),
        "current_location": location_separate[0],
        "destination_location": location_separate[1],
        "gojek_price": gojek_price,
        "tada_price": tada_price,
        "zig_price": zig_price,
    }, query_table)

    userTravelHistory.add_travel_history({
        'user_id': user_id,
        'location': location_separate[0],
        })
    
    userTravelHistory.add_travel_history({
        'user_id': user_id,
        'location': location_separate[1],
    })

    price_query = create_price_query_message(gojek_price, tada_price, zig_price)

    message = await context.bot.edit_message_text(
        price_query,
        update.effective_chat.id,
        message.message_id,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
