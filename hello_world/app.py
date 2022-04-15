from cerberus import Validator
from json.decoder import JSONDecodeError
import boto3
import uuid
import json
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key
from http_response import HttpResponse


table_name = os.environ.get('TABLE', 'user')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)


user_schema = {
    'name': {
        'required': True,
        'type': 'string',
        'minlength': 2,

    },
    'age': {
        'required': True,
        'type': 'string',
     
    },
    'email': {
        'required': True,
        'type': 'string',
        'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
        
    },
    'role': {
        'required': True,
        'type': 'string',
        'allowed': ['admin', 'superAdmin'],
    }
}




def lambda_handler(event, context):
    ret = None
    if event['httpMethod'] == 'GET':
        if event['pathParameters'] is not None:
            ret = getById(event)
        else:
            ret = getAll()
    elif event['httpMethod'] == 'DELETE':
        ret = deleteOne(event)
    elif event['httpMethod'] == 'POST':
        ret = postUser(event)
    elif event['httpMethod'] == 'PUT':
        ret = putUser(event)
    else :
        return HttpResponse.conflict({  "message": '"unsupported http methode"'})
    return ret

def postUser(event):

    try:
      doc = json.loads(event['body'])
    except JSONDecodeError:
        return HttpResponse.bad_request('Could not decode JSON body')


    user_validator = Validator(user_schema)
    if not user_validator.validate(doc):
        msg = user_validator.errors
        return HttpResponse.bad_request({"error": '{}'.format(msg)})


    id_item = str(uuid.uuid1())
    created_date = datetime_to_string(datetime.utcnow())
    doc["created_date"] = created_date
    doc['id'] = id_item
    
    try:
         table.put_item(TableName=table_name, Item=doc)

    except Exception as e :
         return HttpResponse.bad_request({"error": '{}'.format(e)})
    return HttpResponse.success({ "userId": '{}'.format(id_item)})

def getById(event):
        user_id =event['pathParameters']['id']
        response = table.query(KeyConditionExpression=Key('id').eq(user_id))
        items = response['Items']
        return HttpResponse.success(items[0])

def getAll():
    response = table.scan()
    return HttpResponse.success(response['Items'])

def deleteOne(event):
        user_id =event['pathParameters']['id']
        old_item = getById(event)

        try:
            if not old_item:
                raise Exception("Item not found.")
            else:
                table.delete_item(Key={'id': user_id})
        except Exception as e:
            return HttpResponse.bad_request({"error": '{}'.format(e)})
        return HttpResponse.success({  "message": '"deleted successfully"'})


def putUser(event):
    try:
      doc = json.loads(event['body'])
    except JSONDecodeError:
        return HttpResponse.bad_request('Could not decode JSON body')


    user_validator = Validator(user_schema)
    if not user_validator.validate(doc):
        msg = user_validator.errors
        return HttpResponse.bad_request({"error": '{}'.format(msg)})

    updated_date = datetime_to_string(datetime.utcnow())
    doc["updated_date"] = updated_date
    doc["id"] =event['pathParameters']['id']

    try:
         table.put_item(TableName=table_name, Item=doc)

    except Exception as e :
        return HttpResponse.bad_request({"error": '{}'.format(e)})
    return HttpResponse.success({  "message": '"updated successfully"'})



DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
def datetime_to_string(datetime_object):
    return datetime_object.strftime(DATE_TIME_FORMAT)
