# Takes file from S3, transcribes it, 
# and returns transcription to S3

import requests
import json
import boto3
import os
import whisper
from config import *

# Gets S3 client
def get_s3_client(credentials_http_path):
    r = requests.get(credentials_http_path)
    credentials = json.loads(r.text)
    return boto3.client('s3', 
                      aws_access_key_id=credentials['AccessKeyId'], 
                      aws_secret_access_key=credentials['SecretAccessKey'], 
                      aws_session_token=credentials['Token'])

# Transcribe expects:
# - 'file': a flac file with 16,000 hertz sample rate
# - 'language': a string with the language code for whisper, if None, it will auto detect
# - 'task': either 'transcribe' or 'translate'. If 'translate', it will translate to English.
def transcribe(model_type, file_name, language, task):
    model = whisper.load_model(model_type)
    transcription = model.transcribe(file_name,
                                    language=language, 
                                    task=task)
    return transcription

def stores_dict_in_json_file(dictionary, file_name):
    result_json = json.dumps(dictionary)
    with open(file_name, 'w') as f:
        f.write(result_json)

if __name__ == "__main__":
    s3 = get_s3_client(S3_CREDENTIALS_PATH)
    
    # Download file from the bucket
    file_name = os.environ['FILE_NAME']
    s3.download_file(S3_BUCKET, 
                     file_name, 
                     file_name)

    # Transcribes file
    result = transcribe(WHISPER_MODEL,
                        file_name,
                        os.environ['LANGUAGE'],
                        os.environ['TASK'])

    # Stored dict in json file 
    json_file_name = file_name+'_result.json'
    stores_dict_in_json_file(result, json_file_name)

    # Uploads json file to S3
    s3.upload_file(json_file_name,
                   S3_BUCKET,
                   json_file_name)

