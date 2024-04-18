import boto3
import requests
from bot.conversations.save import save
from bot.messages.bookmark import create_saved_bookmark_message
from bot.messages.invalid import create_invalid_check
from bot.messages.price_query import create_choose_end, create_choose_start, create_loading_message, create_price_query_message
import xml.etree.ElementTree as ET
from telegram.ext import (
    ContextTypes,
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
from bot.repository import (
    user as db_user,
    query as db_query,
    userTravelHistory as db_userTravelHistory,
    bookmark as db_bookmark,
)

from bot.utils.helper import get_epoch_time, getAd, has_received_ad,get_current_date

from ..api.price import (
    get_dest_addr_ref,
    get_gojek_price,
    get_tada_price,
    get_zig_price,
)

from bot.conversations.convo import handle_ad_convo

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')
query_table = ddb_resource.Table('Query')
user_travel_history_table = ddb_resource.Table('UserTravelHistory')
ads_table = ddb_resource.Table('Ads')
bookmark_table = ddb_resource.Table('Bookmark')

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["location1"] = None
    context.user_data["location2"] = None

    user_input = update.message.text.lower()
    user = update.message.from_user
    context.user_data["id"] = user.id
    context.user_data["first_name"] = user.first_name
    context.user_data["username"] = user.username

    # ERROR HERE PLS FIX
    if not db_user.user_exists(user.id,user_table):
        db_user.create_user({
        "user_id": user.id,
        "name": user.first_name,
        "username": user.username
    },user_table)

    # format is <location1> to <location2>, separate locations using "to"
    # ERROR HERE PLS FIX
    db_user.update_check_command(user.id,user_table)
    locations_input = user_input[len("/check") :].strip()
    locations = locations_input.split(" to ")

    if len(locations) <= 1 and locations[0] == '':
        response = create_invalid_check()
        await update.message.reply_text(response)
        return START_ROUTES
    
    if len(locations) >= 1:
        location1 = locations[0].strip()
        context.user_data["location1"] = location1

    if len(locations) >= 2:
        location2 = locations[1].strip()
        context.user_data["location2"] = location2


    try:
        loc1_data = get_dest_addr_ref(location1)
        # print("check function's: loc1_data", loc1_data)
        reply_keyboard = [[location["name"]] for location in loc1_data]
        keyboardMarkup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        context.user_data["loc1_data"] = loc1_data
    except Exception as e:
        print("An error occured at check:", e)
        return "An error occurred: {}".format(e)

    await update.message.reply_text(
        create_choose_start(), reply_markup=keyboardMarkup
    )

    return SELECT_START_LOCATION


async def handle_start_live_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if update is None or update.message is None or update.message.location is None:
        print("detected none?")
        return 3
    lat = update.message.location.latitude
    lng = update.message.location.longitude
    
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}'
    resp = requests.get(url)
    root = ET.fromstring(resp.text)
    location1 = root.find("result").text.strip()
    context.user_data["location1"] = location1
    context.user_data["location2"] = None

    try:
        loc1_data = get_dest_addr_ref(location1)
        # print("check function's: loc1_data", loc1_data)
        reply_keyboard = [[location["name"]] for location in loc1_data]
        keyboardMarkup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        context.user_data["loc1_data"] = loc1_data
    except Exception as e:
        print("An error occured at check:", e)
        return "An error occurred: {}".format(e)

    await update.message.reply_text(
        create_choose_start(), reply_markup=keyboardMarkup
    )

    return SELECT_START_LOCATION

async def select_start_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    location1 = update.message.text
    # find the addrRef from the loc1_data using location1 as reference
    loc1_data = context.user_data["loc1_data"]
    loc1_data = [location for location in loc1_data if location["name"] == location1]
    context.user_data["loc1_addr_ref"] = loc1_data[0]["addrRef"]
    context.user_data["loc1_lat"] = loc1_data[0]["addrLat"]
    context.user_data["loc1_lng"] = loc1_data[0]["addrLng"]
    context.user_data["loc1"] = location1
    # insert_interaction(context.user_data["id"], 'select_start_location')

    # get_dest_addr_ref for location2
    location2 = context.user_data.get("location2", None)
    
    if location2 is None:
        await update.message.reply_text("Choose your end location by sending a live location or the location name")
        # ask for live location or real location
        return 3
        
    try:
        loc2_data = get_dest_addr_ref(context.user_data["location2"])
        context.user_data["loc2_data"] = loc2_data
        reply_keyboard = [[location["name"]] for location in loc2_data]
        keyboardMarkup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            create_choose_end(),
            reply_markup=keyboardMarkup,
        )
        return SELECT_END_LOCATION
    except Exception as e:
        await update.message.reply_text("Sorry an error occured! Try again")
        return START_ROUTES

async def select_end_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update is None or update.message is None or update.message.location is None:
        print("detected none?")
        return 3
    lat = update.message.location.latitude
    lng = update.message.location.longitude
    
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}'
    resp = requests.get(url)
    root = ET.fromstring(resp.text)
    location2 = root.find("result").text.strip()
    context.user_data["location2"] = location2

    try:
        loc2_data = get_dest_addr_ref(context.user_data["location2"])
        context.user_data["loc2_data"] = loc2_data
        reply_keyboard = [[location["name"]] for location in loc2_data]
        keyboardMarkup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            create_choose_end(),
            reply_markup=keyboardMarkup,
        )
        return SELECT_END_LOCATION
    except Exception as e:
        await update.message.reply_text("Sorry an error occured! Try again")
        return START_ROUTES

async def on_send_end_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location2"] = update.message.text
    try:
        loc2_data = get_dest_addr_ref(context.user_data["location2"])
        context.user_data["loc2_data"] = loc2_data
        reply_keyboard = [[location["name"]] for location in loc2_data]
        keyboardMarkup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            create_choose_end(),
            reply_markup=keyboardMarkup,
        )
        return SELECT_END_LOCATION
    except Exception as e:
        await update.message.reply_text("Sorry an error occured! Try again")
        return START_ROUTES

async def select_end_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # insert_interaction(context.user_data["id"], 'select_end_location')
    location2 = update.message.text
    loc2_data = context.user_data["loc2_data"]
    loc2_data = [location for location in loc2_data if location["name"] == location2]
    context.user_data["loc2_addr_ref"] = loc2_data[0]["addrRef"]
    context.user_data["loc2_lat"] = loc2_data[0]["addrLat"]
    context.user_data["loc2_lng"] = loc2_data[0]["addrLng"]
    context.user_data["loc2"] = location2
    
    if context.user_data.get("isAdd", False):
        location_name = context.user_data["loc1"] + "|||" + context.user_data["loc2"]
        location_addr_ref = context.user_data["loc1_addr_ref"] + ";" + context.user_data["loc2_addr_ref"]
        location_coords = context.user_data["loc1_lat"] + "," + context.user_data["loc1_lng"] + ";" + context.user_data["loc2_lat"] + "," + context.user_data["loc2_lng"]
        item = {
            "user_id": context.user_data["id"],
            "timestamp": get_epoch_time(),
            "location_name": location_name,
            "location_addr_ref": location_addr_ref,
            "location_coords": location_coords,
        }
        success = db_bookmark.create_bookmark(item, bookmark_table)
        if success["success"]:
            message = await update.message.reply_text(create_saved_bookmark_message())
        context.user_data["isAdd"] = False
        return START_ROUTES
    else:
        await end_routes(update, context)
        result = await get_ads(update, context)
        if result is None:
            return START_ROUTES
        
        ad_content = await handle_ad_convo(update,context,result["ad_content"])

        await update.message.chat.send_photo(
            photo=result["photo_url"],
            caption=ad_content
            )
        return START_ROUTES

async def get_ads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    result = getAd(context.user_data["id"], {
        "user_table": user_table,
        "user_travel_history_table": user_travel_history_table,
        "query_table": query_table,
        "ad_table": ads_table,
    })


    if result is None or has_received_ad(context.user_data["id"], user_table):
        return None
    current_date = get_current_date() 
    db_user.update_ad_received(context.user_data["id"], current_date,user_table)
    return result


async def end_routes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    location1 = context.user_data["location1"]
    location2 = context.user_data["location2"]

    loc1_addr_ref = context.user_data["loc1_addr_ref"]
    loc2_addr_ref = context.user_data["loc2_addr_ref"]

    loc1_lat = context.user_data["loc1_lat"]
    loc1_lng = context.user_data["loc1_lng"]
    loc2_lat = context.user_data["loc2_lat"]
    loc2_lng = context.user_data["loc2_lng"]

    user_id = context.user_data["id"]
    # insert_interaction(user_id, 'end_routes')
    comb_loc_1=context.user_data["loc1_lat"]+","+context.user_data["loc1_lng"]
    comb_loc_2=context.user_data["loc2_lat"]+","+context.user_data["loc2_lng"]
    
    response = create_loading_message()
    message = await update.message.reply_text(response)
    gojek_price = get_gojek_price(
        float(loc1_lat), float(loc1_lng), float(loc2_lat), float(loc2_lng)
    )
    tada_price = get_tada_price(loc1_lat, loc1_lng, loc2_lat, loc2_lng)
    zig_price = get_zig_price(
        loc1_lat, loc1_lng, loc1_addr_ref, loc2_lat, loc2_lng, loc2_addr_ref
    )
    
    
    gojek_price = "{:.2f}".format(gojek_price / 100.0)
    tada_price = "{:.2f}".format((tada_price))
    # ERROR HERE PLS FIX

    db_query.create_query({
        "user_id": user_id,
        'timestamp': get_epoch_time(),
        "current_location": location1,
        "destination_location": location2,
        "gojek_price": gojek_price,
        "tada_price": tada_price,
        "zig_price": zig_price,
    }, query_table)

    db_userTravelHistory.add_travel_history({
        "user_id": user_id,
        "location":comb_loc_1,
    }, user_travel_history_table)

    db_userTravelHistory.add_travel_history({
        "user_id": user_id,
        "location":comb_loc_2,
    }, user_travel_history_table)

    Inlinekeyboard = [
        [
            InlineKeyboardButton(
                "Open in Gojek",
                url="https://proxy-206.vercel.app/?scheme=gojek&path=x/",
            ),
            # callback_data=lambda _: insert_interaction(user_id, 'end_routes.open_gojek')
            # callback_data=('end_routes.open_gojek', user_id)
            InlineKeyboardButton(
                "Open in Tada",
                url="https://proxy-206.vercel.app/?scheme=tadaglobal&path=x/",
            )
            # callback_data=lambda _: insert_interaction(user_id, 'end_routes.open_tada')
            # callback_data=('end_routes.open_tada', user_id)
            # )
            ,
            InlineKeyboardButton(
                "Open in Zig",
                url="https://proxy-206.vercel.app/?scheme=comfortdelgrotaxi&path=x/",
            ),
            # callback_data=lambda _: insert_interaction(user_id, 'end_routes.open_grab')
            # callback_data=('end_routes.open_grab', user_id)
            # ),
        ],
        [InlineKeyboardButton("Save to bookmarks", callback_data='save_bookmark')],
    ]
    

    price_query = create_price_query_message(gojek_price, tada_price, zig_price)
    message = await context.bot.edit_message_text(
        price_query,
        update.effective_chat.id,
        message.message_id,
        reply_markup=InlineKeyboardMarkup(Inlinekeyboard),
    )
    return START_ROUTES

