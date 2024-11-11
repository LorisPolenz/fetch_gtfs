import io
import os
import gzip
import requests
from minio import Minio
from datetime import datetime

TIMESTAMP = round(datetime.now().timestamp())
REQUEST_URL = 'https://api.opentransportdata.swiss/gtfsrt2020'
PARAMS = {
    "format": "json",
}
HEADERS = {
    "Accept-Encoding": "gzip, depflate",
    "Authorization": f"Bearer {os.getenv('OPEN_DATA_API_KEY')}",
}

# Initialize the S3 client
s3_client = Minio(os.getenv('S3_ENDPOINT'),
                  os.getenv('S3_ACCESS_KEY'),
                  os.getenv('S3_SECRET_KEY'),
                  secure=True)

# Get the data
response = requests.get(REQUEST_URL, params=PARAMS, headers=HEADERS)
response.raise_for_status()
compressed_data = gzip.compress(response.content)


# Compress the data
compressed_data = io.BytesIO()
with gzip.GzipFile(fileobj=compressed_data, mode='wb') as gz:
    gz.write(response.content)
compressed_data.seek(0)

# Upload the data to S3
s3_client.put_object(
    bucket_name=os.getenv('S3_BUCKET_GTFS_RT'),
    object_name=f"{TIMESTAMP}_gtfs-rt.json.gz",
    data=compressed_data,
    length=compressed_data.getbuffer().nbytes,
    content_type="application/gzip")

print(f"{TIMESTAMP}_gtfs-rt.json.gz")
