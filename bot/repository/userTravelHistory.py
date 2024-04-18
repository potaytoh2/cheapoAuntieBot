import boto3
import bot.utils.helper as helper

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

default_table = ddb_resource.Table('UserTravelHistory')

def get_user_travel_history(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            }
        )
        return response['Items']
    except Exception as e:
        return None
    
def get_user_travel_history_by_location(user_id,location,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            KeyConditionExpression='user_id = :user_id and location = :location',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':location': location
            }
        )
        return response['Items']
    except Exception as e:
        return None
    
def update_occurence(user_id,location,table=None):
    if table is None:
        table = default_table
    try:
        response = table.update_item(
            Key={
                'user_id': user_id,
                'location': location
            },
            UpdateExpression="set occurence = occurence + :val",
            ExpressionAttributeValues={
                ':val': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']
    except Exception as e:
        return None

def add_travel_history(item,table=None):
    if table is None:
        table = default_table
    try:
        response = get_user_travel_history_by_location(item['user_id'],item['location'],table)
        if response is not None and len(response) > 0:
            response = update_occurence(item['user_id'],item['location'],table)
            if response is not None:
                return {"success": True, "message": "Travel history updated successfully."}
        else:
            response = get_user_travel_history(item['user_id'],table)
            if response is not None and len(response) > 0:
                for travel_history in response:
                    if helper.within_2_km(travel_history['location'],item['location']):
                        response = update_occurence(item['user_id'],travel_history['location'],table)
                        if response is not None:
                            return {"success": True, "message": "Travel history updated successfully."}
            table.put_item(
                Item={
                    'user_id': item['user_id'],
                    'location': item['location'],
                    'occurence': 1
                }
            )
            return {"success": True, "message": "Travel history added successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
    
def get_user_frequent_locations(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            },
            IndexName='occurence_index',
            ScanIndexForward=False, 
            Limit=3 
        )
        return response['Items']
    except Exception as e:
        return None