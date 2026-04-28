import os
import json

import ibm_boto3 
from ibm_botocore.client import Config

COS_API_KEY = os.getenv("COS_API_KEY")
COS_INSTANCE_CRN = os.getenv("COS_INSTANCE_CRN")
COS_ENDPOINT = os.getenv("COS_ENDPOINT")
BUCKET_NAME = os.getenv("IBM_BUCKET")

cos = ibm_boto3.client(
    service_name="s3",
    ibm_api_key_id=COS_API_KEY,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version='oauth'),
    endpoint_url=COS_ENDPOINT
)

def get_stored_json_data(file_name: str) -> dict:
    print(f"Accessing IBM Cloud Object Storage - {file_name}", flush=True)
    response = cos.get_object(Bucket=BUCKET_NAME, Key=file_name)
    data = response["Body"].read()
    data_dict = json.loads(data.decode('utf-8'))
    return data_dict

def save_json_data(file_name: str, updated_data: dict) -> None:
    print(f"Saving to IBM Cloud Object Storage - {file_name}", flush=True)
    data_as_str = json.dumps(updated_data, indent=4)
    cos.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=data_as_str.encode('utf-8'))