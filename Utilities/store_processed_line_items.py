import json
from typing import List

from Shopify_API.execute_api_call import execute_api_call
from GraphQL_Operations.get_gql_op import get_gql_op

def build_processed_ids_list(processed_ids_dict: dict, metafld_key: str) -> List[dict]:
    processed_ids_list = []
    for order_id in processed_ids_dict:
        shopify_ids = processed_ids_dict[order_id]
        if shopify_ids:
            processed_ids_list.append({
                "Order ID": order_id,
                "Metafield Key": metafld_key,
                "Shopify IDs": shopify_ids
            })
    return processed_ids_list

def store_processed_line_items(shopify_ids_rows: List[dict]) -> None:
    order_metafields_mutation = get_gql_op("store_processed_line_items")
    input_data = {
        "metafields": []
    }
    metafields_to_store = input_data["metafields"]
    for row in shopify_ids_rows:
        order_id = row["Order ID"]
        metafield_key = row["Metafield Key"]
        line_items = row["Shopify IDs"]
        unique_line_items = list(set(line_items))
        order_id_num = order_id.split("/")[-1]
        print(f"Order {order_id_num} - Storing {len(unique_line_items)} Total Processed Line Items ({metafield_key})", flush=True)
        metafields_to_store.append({
            "ownerId": order_id,
            "namespace": "custom",
            "key": metafield_key,
            "value": json.dumps(unique_line_items)
        })
        if len(metafields_to_store) == 25:
            execute_api_call(order_metafields_mutation, input_data)
            print(f"API Call Made - Storing {len(metafields_to_store)} Metafields", flush=True)
            metafields_to_store.clear()
    if metafields_to_store:
        execute_api_call(order_metafields_mutation, input_data)
        print(f"API Call Made - Storing {len(metafields_to_store)} Metafields", flush=True)