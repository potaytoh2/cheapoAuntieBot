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

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    message_text = update.message.text
    
    # Parse the input to extract the bookmark ID
    try:
        bookmark_id = int(message_text.split()[-1])
    except ValueError:
        await update.message.reply_text("Invalid input. Please provide a valid bookmark ID.")
        return START_ROUTES
    
    try:
        # Get the bookmark with the specified ID
        bookmark_to_remove = db_bookmark.get_bookmark_by_num_id(user_id, bookmark_id)
        if not bookmark_to_remove:
            await update.message.reply_text("Bookmark not found.")
            return START_ROUTES
        
        # Remove the bookmark
        result = db_bookmark.remove_bookmark(user_id, bookmark_id)
        if result["success"]:
            await update.message.reply_text(f"Bookmark {bookmark_id} removed successfully.")
        else:
            await update.message.reply_text(f"Failed to remove bookmark {bookmark_id}: {result['message']}")
            
    except Exception as e:
        print("Error removing bookmark:", e)
        await update.message.reply_text("An error occurred while removing the bookmark.")
        
    return START_ROUTES
