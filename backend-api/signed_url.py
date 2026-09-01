import json
from google.cloud import storage, secretmanager
from google.oauth2 import service_account
from datetime import timedelta

def get_service_account_key(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/708196257066/secrets/align-google-credentials/versions/1"
    response = client.access_secret_version(request={"name": name})
    secret_payload = response.payload.data.decode("UTF-8")
    return json.loads(secret_payload)

def generate_signed_url(bucket_name, blob_name, duration, credentials):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(seconds=10),
        method="GET",
    )

    return url

if __name__ == "__main__":
    secret_id = "align-google-credentials"
    bucket_name = "align-hvl-2024-release1"
    blob_name = "exp3_ferranti_effect/ferranti_effect.glb"
    duration = 6  # URL valid for 365 days

    # Fetch the service account key from Secret Manager
    service_account_info = get_service_account_key(secret_id)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Generate the signed URL
    signed_url = generate_signed_url(bucket_name, blob_name, duration, credentials)
    print(f"Generated signed URL: {signed_url}")
