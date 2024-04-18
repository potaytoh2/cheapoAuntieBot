import boto3
from botocore.exceptions import ClientError
ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

default_table = ddb_resource.Table('User')

#add user to db
def create_user(item,table=None):
    print(item)
    if table is None:
        table = default_table
    if(user_exists(item['user_id'],table)):
        return {"success": False, "message": "User already exists."}
    try:
        table.put_item(
            Item=item
        )
        return {"success": True, "message": "User added successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_user(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )
        return response['Item']
    except Exception as e:
        return None

def update_check_command(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set queries = if_not_exists(queries, :init) + :val",
            ExpressionAttributeValues={
                ':init': 0,
                ':val': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'queries' in response['Attributes']:
            new_queries = response['Attributes']['queries']
            return {"success": True, "new_queries": new_queries}
        else:
            return {"success": False, "message": "queries was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_app_clicks(user_id,spend,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set app_clicks = if_not_exists(app_clicks, :init_clicks)+ :val, spend = if_not_exists(spend,:init_spend)+ :spend",
            ExpressionAttributeValues={
                ':init_clicks': 0,
                ':init_spend': 0,
                ':val': 1,
                ':spend': spend
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'app_clicks' in response['Attributes'] and 'spend' in response['Attributes']:
            new_app_clicks = response['Attributes']['app_clicks']
            new_spend = response['Attributes']['spend']
            return {"success": True, "new_app_clicks": new_app_clicks, "new_spend": new_spend}
        else:
            return {"success": False, "message": "app_clicks was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_ad_sent(user_id, table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set ads_sent = if_not_exists(ads_sent,:init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'ads_sent' in response['Attributes']:
            new_ads_sent = response['Attributes']['ads_sent']
            return {"success": True, "new_ads_sent": new_ads_sent}
        else:
            return {"success": False, "message": "ads_sent was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_ad_clicks(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="SET ad_clicks = if_not_exists(ad_clicks, :init) + :val",
            ExpressionAttributeValues={
                ':init': 0,
                ':val': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'ad_clicks' in response['Attributes']:
            new_clicks = response['Attributes']['ad_clicks']
            return {"success": True, "new_ad_clicks": new_clicks}
        else:
            return {"success": False, "message": "ad_clicks was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_start_command(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set start_command = if_not_exists(start_command, :init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'start_command' in response['Attributes']:
            new_start_command = response['Attributes']['start_command']
            return {"success": True, "new_start_command": new_start_command}
        else:
            return {"success": False, "message": "start_command was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_add_command(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set add_command = if_not_exists(add_command, :init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'add_command' in response['Attributes']:
            new_add_command = response['Attributes']['add_command']
            return {"success": True, "new_add_command": new_add_command}
        else:
            return {"success": False, "message": "add_command was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def update_save_button(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set save_button = if_not_exists(save_button, :init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'save_button' in response['Attributes']:
            new_save_button = response['Attributes']['save_button']
            return {"success": True, "new_save_button": new_save_button}
        else:
            return {"success": False, "message": "save_button was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def update_list_command(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set list_command = if_not_exists(list_command, :init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'list_command' in response['Attributes']:
            new_list_command = response['Attributes']['list_command']
            return {"success": True, "new_list_command": new_list_command}
        else:
            return {"success": False, "message": "list_command was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def update_bookmark_call(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set bookmark_call = if_not_exists(bookmark_call, :init)+ :val",
            ExpressionAttributeValues={
                ':val': 1,
                ':init': 0
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'bookmark_call' in response['Attributes']:
            new_bookmark_call = response['Attributes']['bookmark_call']
            return {"success": True, "new_bookmark_call": new_bookmark_call}
        else:
            return {"success": False, "message": "bookmark_call was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def remove_user(user_id,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.delete_item(
            Key={
                'user_id': user_id
            }
        )
        # If no exception is raised, the deletion was successful
        return {"success": True, "message": "User removed successfully."}
    except ClientError as e:
        # An exception occurred, indicating the deletion was not successful
        return {"success": False, "message": e.response['Error']['Message']}


def user_exists(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )
        if 'Item' in response:
            return True
        else:
            return False
    except Exception as e:
        return False
    
def update_ad_received(user_id,new_date,table=None):
    if table is None:
        table = default_table
    if(not user_exists(user_id,table)):
        return {"success": False, "message": "User does not exist."}
    try:
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set ads_received_date = :new_date",
            ExpressionAttributeValues={
                ':new_date': new_date
            },
            ReturnValues="UPDATED_NEW"
        )
        if 'Attributes' in response and 'ads_received' in response['Attributes']:
            new_ads_received = response['Attributes']['ads_received']
            return {"success": True, "new_ads_received": new_ads_received}
        else:
            return {"success": False, "message": "ads_received was not updated."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_ad_received(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )
        if 'Item' in response:
            return response['Item']['ads_received_date']
        else:
            return None
    except Exception as e:
        return None