from typing import List

from Shopify_API.execute_api_call import execute_api_call
from GraphQL_Operations.get_gql_op import get_gql_op

def get_orders_to_process(updated_since_timestamp: str) -> List[tuple]:
    orders_query = get_gql_op("lookup_orders")
    orders_query_cursor = None
    query_has_next_page = True
    orders = []
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
            order_tuple = (order["id"], order["name"], order["createdAt"])
            orders.append(order_tuple)
        query_has_next_page = orders_res["orders"]["pageInfo"]["hasNextPage"]
        orders_query_cursor = orders_res["orders"]["pageInfo"]["endCursor"]
    return orders