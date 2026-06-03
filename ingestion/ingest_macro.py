import os
import json
import requests
import oci
from datetime import datetime
from dotenv import load_dotenv

# 1. Load the hidden environment variables
load_dotenv()
API_KEY = os.getenv("FRED_API_KEY")

# We will pull the Effective Federal Funds Rate (FEDFUNDS) as our test macro indicator
SERIES_ID = "FEDFUNDS" 
URL = f"https://api.stlouisfed.org/fred/series/observations?series_id={SERIES_ID}&api_key={API_KEY}&file_type=json"

# 2. OCI Configuration (Matches your Terraform deployment!)
NAMESPACE = "axhrcbgwo7cd"
BUCKET_NAME = "portfolio_data_lake"

def fetch_macro_data():
    print(f"[*] Fetching {SERIES_ID} data from FRED API...")
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def upload_to_oci(data):
    print("[*] Authenticating with Oracle Cloud via ~/.oci/config...")
    # This automatically reads your hidden config file and RSA key!
    config = oci.config.from_file()
    object_storage = oci.object_storage.ObjectStorageClient(config)

    # Create a dynamic file name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"bronze/macro/fred_{SERIES_ID}_{timestamp}.json"

    print(f"[*] Streaming data to OCI Object Storage: {file_name}")
    object_storage.put_object(
        namespace_name=NAMESPACE,
        bucket_name=BUCKET_NAME,
        object_name=file_name,
        put_object_body=json.dumps(data)
    )
    print("[+] Ingestion successfully completed!")

if __name__ == "__main__":
    if not API_KEY or API_KEY == "your_api_key_here":
        print("[-] Error: Please update your .env file with a valid FRED API key.")
    else:
        raw_data = fetch_macro_data()
        upload_to_oci(raw_data)
