import boto3
from bot.messages.bookmark import create_list_bookmark_message
from telegram.ext import (
    ContextTypes,
)
from bot.repository import (
    bookmark as db_bookmark
)
from telegram import Update
from bot.repository import (
    user as db_user,
    query as db_query,
    userTravelHistory as db_userTravelHistory,
    bookmark as db_bookmark,
)
ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')
query_table = ddb_resource.Table('Query')
user_travel_history_table = ddb_resource.Table('UserTravelHistory')
bookmark_table = ddb_resource.Table('Bookmark')
START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

bookmark_table = ddb_resource.Table('Bookmark')


async def listBookmarks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    # insert_interaction(user_id, 'list')

    try:
        responses = db_bookmark.get_all_bookmark_by_user_id(user_id, bookmark_table)
        path_list = create_list_bookmark_message()
        print(responses)
        for response in responses:
            location_name = response["location_name"].split("|||")
            if (len(location_name) < 2): continue
            path_list += f"/{response['num_id']}. {location_name[0]} -> {location_name[1]}\r\n"
        await update.message.reply_text(path_list)
    except Exception as e:
        print("Error listing bookmarks", e)
    return START_ROUTES