import json
import boto3
import os
import logging
import time
import urllib3
import traceback
import pickle, sys 
from botocore.exceptions import ClientError

http = urllib3.PoolManager()
timestamp = int(round(time.time() * 1000))
current_milli_time = lambda: int(round(time.time() * 1000))
HTTP = urllib3.PoolManager()
timestr = time.strftime("%Y%m%d_%H%M%S")
bucket_name = os.environ.get('BUCKET_NAME')
bucket_name = 'sports-odd-lnding'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def send_sns(message):

    logger.info(f"Executing send_sns() Function ")

    sns_client = boto3.client("sns")
    topic_arn = os.environ.get('TOPIC_ARN')
    subject = 'Meessage from SPORTS ODDS API'
    
    try:
        sent_message = sns_client.publish(
                TargetArn=topic_arn,
                Message=json.dumps(message,indent=4),
                Subject=subject
        )
        if sent_message is not None:
            logger.info(f"Success - Message ID: {sent_message['MessageId']}")
        return {
            "statusCode": 200,
            "body": "Error message sent to SNS successfully"
        }
    except ClientError as e:
        logger.error(e)
        return None

# To retrive the API key from AWS secrets manager
def get_secret():

    logger.info("retreving API secret Key from AWS Secret Manager")
    secret_name = "X-RapidAPI-Key"
    region_name = "ap-southeast-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error(e)
        message = 'There was an error while retriving the API key from screts manager'
        message = json.dumps({ 'Status' : 400,
                     'Error' : str(e)},indent=4)        
        response = send_sns(message)
        return response
        return None

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret


def download_sports_odd(secret_key,my_bucket):
    #fuction to download the sports ODD data
    sign_up_key =  secret_key['X-RapidAPI-Key']
    

    url = "https://odds.p.rapidapi.com/v4/sports"
    logger.info("Calling the API URL")
    
    querystring = {"all":"true"}
    headers = {
        "X-RapidAPI-Key": sign_up_key,
        "X-RapidAPI-Host": "odds.p.rapidapi.com"
    }
    # Calling HTTP GET Method
    # Information about the API found here https://rapidapi.com/theoddsapi/api/live-sports-odds/ 
    # Subscribe with email ID to get the API Access Key
    try:
        request = http.request(
                    "GET",
                    url,
                    headers=headers, 
                    fields=querystring,
                    retries=urllib3.util.Retry(3),
            )
        data = json.loads(request.data.decode("utf8"))
        key = upload_data_to_s3(data,my_bucket)
        response = { 'statusCode': 200,
                     'records_count': len(data) 
                    }
        return response

    except KeyError as e:
        logger.error(f"Wrong format url", e)
        message = 'Wrong Url format'
        message = json.dumps({ 'Status' : 400,
                     'Error' : str(e)},indent=4)        
        response = send_sns(message)
        return response
        
    except urllib3.exceptions.MaxRetryError as e:
        logger.error("API unavailable")
        message = json.dumps({ 'Status' : 400,
                     'Error' : str(e)})        
        response = send_sns(message)
        return response

def upload_data_to_s3(data,my_bucket):
    key = 'RAW/' + 'sports_odds' + '_' + timestr + '.json'
    my_bucket.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data))
        
    return key

def put_logs(client,logGroupName, logStreamName, message):
    ####### Not in use ######
    log_event = {
        'timestamp': int(time.time()) * 1000,
        'message': message
    }

    client.put_log_events(
        logGroupName = logGroupName,
        logStreamName = logStreamName,
        logEvents = [log_event])
    return log_event

def lambda_handler(event, context):
    secret_key = get_secret()
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket_name)
    response = download_sports_odd(secret_key,my_bucket)
    return response
