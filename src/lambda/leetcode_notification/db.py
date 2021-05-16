import time
import boto3


import constants
import utils

db_client = boto3.client('dynamodb')


def get_problems(date_):
    # today = utils.get_today()
    paginator = db_client.get_paginator('query')
    response_iterator = paginator.paginate(
        TableName=constants.DYNAMODB_TABLE,
        KeyConditionExpression='#date = :date',
        ExpressionAttributeValues={':date': {'S': date_}},
        ExpressionAttributeNames={'#date': 'date'}
    )
    problems = []
    for response in response_iterator:
        for item in response['Items']:
            status, slug, id_ = item['version']['S'].split('#')
            problems.append((slug, id_, status))
    return problems


def store_problems(date_, slug, id_, status):
    expire_after = 24*2*60*60 + int(time.time())
    response = db_client.put_item(
        TableName=constants.DYNAMODB_TABLE,
        Item={
            'date': {'S': date_},
            'version': {'S': f'{status}#{slug}#{id_}'},
            'expire_after': {'N': str(expire_after)}
        }
    )
