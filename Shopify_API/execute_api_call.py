import http.client
import os
import socket
import requests
import time
import urllib3

from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportServerError, TransportQueryError

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
ACCESS_TOKEN = os.getenv("SHOPIFY_TOKEN")
API_VERSION = "2026-04"
GRAPHQL_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/graphql.json"

def create_client() -> Client:
    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL,
        headers={"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"},
        timeout=30
    )
    return Client(transport=transport, fetch_schema_from_transport=False)

client = create_client()

NETWORK_ERRORS = (
    requests.exceptions.ConnectionError,
    urllib3.exceptions.ProtocolError,
    http.client.RemoteDisconnected,
    socket.error,
    OSError
)

def execute_api_call(executable, variable_vals):
    global client
    for attempt in range(5):
        try:
            response = client.execute(executable, variable_values=variable_vals)
            for primary_key in response:
                if response[primary_key].get("userErrors", []):
                    user_errors = response[primary_key]["userErrors"]
                    print(f"User Error on Shopify API Call - {user_errors}", flush=True)
                    print(f"API Call Input Data - {variable_vals}", flush=True)
            return response
        except TransportServerError as e:
            if "502" in str(e) or "520" in str(e):
                wait_time = 2 ** attempt
                print(f"TransportServerError error on attempt {attempt + 1}. Retrying in {wait_time}s...")
                print(e, flush=True)
                time.sleep(wait_time)
            else:
                print(f"Server error: {e}")
                raise
        except TransportQueryError as e:
            if "Throttled" in str(e):
                wait_time = 2 ** attempt + 1
                print(f"Throttling error on attempt {attempt + 1}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Query error: {e}")
                raise
        except NETWORK_ERRORS as e:
            wait_time = 2 ** attempt
            print(f"Network error on attempt {attempt + 1}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            client = create_client()
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    raise Exception("Failed after 5 tries...")