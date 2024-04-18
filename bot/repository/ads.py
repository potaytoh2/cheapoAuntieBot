import boto3

ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

default_table = ddb_resource.Table('Ads')

def create_ad(item,table=None):
    if table is None:
        table = default_table
    try:
        dynamo_item = {}
        for key, value in item.items():
            if isinstance(value, list) and key == 'locations':
            # Special handling for list of locations
                dynamo_item[key] = {'SS': [str(location) for location in value]}
            else:
            # For other attributes, keep the original format
                dynamo_item[key] = value

        table.put_item(Item=dynamo_item)
        return {"success": True, "message": "Ad added successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_ad_with_id(ad_id,table=None):
    if table is None:
        table = default_table
    try:
        response = table.get_item(
            Key={
                'ad_id': ad_id
            }
        )
        return response['Item']
    except Exception as e:
        return e
        
    
def get_ads_with_company(company,table=None):
    if table is None:
        table = default_table
    try:
        response = table.query(
            IndexName='company_index',
            KeyConditionExpression='company = :company',
            ExpressionAttributeValues={
                ':company': company
            },
            ScanIndexForward=False
        )
        return response['Items'][0]
    except Exception as e:
        return None

def get_all_ads(table=None):
    if table is None:
        table = default_table
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        return None
    
def get_all_ads_sortby_bid(table=None):
    if table is None:
        table = default_table
    try:
        response = table.scan()
        items = response['Items']
        items.sort(key=lambda x: x['ad_bid'], reverse=True)
        return items
    except Exception as e:
        return None
    
def delete_ad(ad_id,date,table=None):
    if table is None:
        table = default_table
    try:
        table.delete_item(
            Key={
                'ad_id': ad_id,
                'date': date
            }
        )
        return {"success": True, "message": "Ad deleted successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}