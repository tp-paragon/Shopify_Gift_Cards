from typing import List
from datetime import datetime

from Shopify_API.execute_api_call import execute_api_call
from GraphQL_Operations.get_gql_op import get_gql_op

def get_orders_to_process(updated_since_timestamp: str) -> List[tuple]:
    orders_query = get_gql_op("lookup_orders")
    orders_query_cursor = None
    query_has_next_page = True
    orders = []
    dt_format = "%Y-%m-%dT%H:%M:%SZ"
    dt_start = datetime.strptime(updated_since_timestamp, dt_format)
    query = (f"updated_at:>={updated_since_timestamp} "
             "AND fulfillment_status:fulfilled "
             "AND delivery_method:pick-up")
    while query_has_next_page:
        orders_query_variables = {
            "query": query,
            "cursor": orders_query_cursor,
        }
        orders_res = execute_api_call(orders_query, orders_query_variables)
        orders_batch = orders_res["orders"]["nodes"]
        for order in orders_batch:
            updated_at = order["updatedAt"]
            dt_order = datetime.strptime(updated_at, dt_format)
            if dt_order < dt_start:
                print(f"Order {order["name"]} is too old - {updated_at}", flush=True)
                continue
            order_tuple = (order["id"], order["name"], order["createdAt"])
            orders.append(order_tuple)
        query_has_next_page = orders_res["orders"]["pageInfo"]["hasNextPage"]
        orders_query_cursor = orders_res["orders"]["pageInfo"]["endCursor"]
    return orders