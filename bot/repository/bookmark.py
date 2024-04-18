import boto3

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

default_table = ddb_resource.Table('Bookmark')

def is_bookmark_existing(user_id,location_name,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            IndexName='location_index',
            KeyConditionExpression='user_id = :user_id AND location_name = :location_name',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':location_name': location_name
                }
            )
        if response['Count'] > 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def create_bookmark(item,table=None):
    if table is None:
        table = default_table
    try:
        if(is_bookmark_existing(item['user_id'],item['location_name'],table)):
            return {"success": False, "message": "Bookmark already exists."}
        
        response = table.query(
            IndexName='timestamp_index',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': item['user_id']
            },
            ScanIndexForward=False,
            Limit=1,
        )
        if response['Count'] == 0:
            num_id = 1
            item['num_id'] = num_id
            table.put_item(Item=item)
            return {"success": True, "message": "First Bookmark added successfully."}
        else:
            num_id = response['Items'][0]['num_id']+1
            item['num_id'] = num_id
            table.put_item(Item=item)
            return {"success": True, "message": "Bookmark added successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_bookmark_by_num_id(user_id,num_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'user_id': user_id,
                'num_id': num_id
            },
        )
        print(response)
        return response['Item']
    except Exception as e:
        return e
    
def get_all_bookmark_by_user_id(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            },
            ScanIndexForward=True
        )
        return response['Items']
    except Exception as e:
        return None


def remove_bookmark(user_id,num_id,table=None):
    if table is None:
        table = default_table
    try:
        table.delete_item(
            Key={
                'user_id': user_id,
                'num_id': num_id
            }
        )
        return {"success": True, "message": "Bookmark removed successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}

