import boto3

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

default_table = ddb_resource.Table('Query')

def create_query(item,table=None):
    if table is None:
        table = default_table
    try:
        table.put_item(
            Item=item
        )
        return {"success": True, "message": "Query added successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_latest_query(user_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            },
            ScanIndexForward=False,
            Limit=1  
        )
        return response['Items'][0]
    except Exception as e:
        return None

def get_query(user_id,timestamp,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'user_id': user_id,
                'timestamp': timestamp
            }
        )
        return response['Item']
    except Exception as e:
        return None
    
def get_all_queries(table=None):
    if table is None:
        table = default_table
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        return None
    
def get_all_user_queries(user_id,table):
    if table is None:
        table = default_table
    try:
        response = table.query(
        KeyConditionExpression='user_id = :user_id',
        ExpressionAttributeValues={
            ':user_id': user_id
        },
        ScanIndexForward=False
    )
        return response['Items']
    except Exception as e:
        return None
