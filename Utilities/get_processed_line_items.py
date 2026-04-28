import json
from typing import List

from Shopify_API.execute_api_call import execute_api_call
from GraphQL_Operations.get_gql_op import get_gql_op

def get_processed_line_items(order_id: str, metafield_key: str) -> List[str]:
    metafield_query_variables = {
        "id": order_id, 
        "metafieldNamespace": "custom",
        "metafieldKey": metafield_key
    }
    processed_line_items_query = get_gql_op("lookup_processed_line_items")
    processed_line_items_res = execute_api_call(processed_line_items_query, metafield_query_variables)
    processed_line_items_data = processed_line_items_res["order"]
    if processed_line_items_data["metafield"]:
        line_item_ids = json.loads(processed_line_items_data["metafield"]["value"])
    else:
        line_item_ids = []
    return line_item_ids