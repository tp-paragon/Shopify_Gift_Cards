from decimal import Decimal
import re
from typing import List

from Shopify_API.execute_api_call import execute_api_call
from GraphQL_Operations.get_gql_op import get_gql_op
from Utilities.handle_timestamp import get_date_time
from Utilities.get_sale_context import get_store

def get_gift_card_nums(order_data: dict) -> List[str]:
    gift_card_nums = []
    events = order_data["events"]["nodes"]
    pattern = re.compile(r'^giftcard\d{2}:\d+$')
    for event in events:
        message = event["message"].lower().strip()
        if not pattern.match(message):
            continue
        prefix, gc_num = message.split(":")
        gc_idx = prefix[-2:]
        if not (gc_idx.isnumeric() and gc_num.isnumeric()):
            print(f"GIFT CARD Reading Error: {message}", flush=True)
        gift_card_nums.append([int(gc_idx), gc_num])
    gift_card_nums.sort(key=lambda item: item[0])
    if gift_card_nums:
        print(f"Gift Card Nums in Comments: {gift_card_nums}", flush=True)
    return [gc_num[1] for gc_num in gift_card_nums]

def get_sale_data(order_id: str) -> dict:
    original_sale_query = get_gql_op("lookup_sold_items")
    query_variables = {"id": order_id}
    original_sale_res = execute_api_call(original_sale_query, query_variables)
    return original_sale_res["order"]

def build_gift_card_sale_rows(order_id: str, processed_line_items: List[str], gift_card_skus: set[str]) -> List[dict]:
    transaction_data = get_sale_data(order_id)
    order_number = transaction_data["name"]
    sales_date, sales_time = get_date_time(transaction_data["createdAt"])
    gift_card_nums = get_gift_card_nums(transaction_data)
    gc_idx = 0
    shipment_num = order_number + "01"
    sales_type = "S"
    source_app = transaction_data["app"]
    retail_location = transaction_data["retailLocation"]
    store = get_store(order_number, source_app, retail_location)

    line_items = transaction_data["lineItems"]["nodes"]
    print(f"Order {order_number} Total # of Line Items: {len(line_items)}", flush=True)
    ward_rows = []
    for line_item in line_items:
        line_item_id = line_item["id"]
        sku = line_item["sku"]
        if line_item_id in processed_line_items or sku not in gift_card_skus:
            continue
        if gc_idx < len(gift_card_nums):
            gift_certificate_num = gift_card_nums[gc_idx]
            gc_idx += 1
        else:
            print(f"Gift Card Sale Error - Not Enough Gift Cards Found in Comments. Order {order_number}", flush=True)
            gift_certificate_num = ""
        item_description = line_item["name"]
        units_sold = line_item["currentQuantity"]
        total_units = line_item["quantity"]
        unfulfilled_units = line_item["unfulfilledQuantity"]
        if units_sold == 0 or unfulfilled_units > 0:
            print(f"No Units! {line_item_id} {sku} | sold: {units_sold} | unfilfilled: {unfulfilled_units}")
            continue
        sell_price = Decimal(line_item["discountedPriceSet"]["presentmentMoney"]["amount"])
        extended_sales_amt = sell_price * units_sold
        ward_row = {
            "store": store,
            "order_number": order_number,
            "upc_sold": sku,
            "item_description": item_description,
            "units_sold": units_sold,
            "sell_price": sell_price,
            "state_tax_flag": "N",
            "state_tax_code": "",
            "state_tax_amt": Decimal("0"),
            "state_tax_percent": Decimal("0"),
            "county_tax_flag": "N",
            "county_tax_code": "",
            "county_tax_amt": Decimal("0"),
            "county_tax_percent": Decimal("0"),
            "local_tax_flag": "N",
            "local_tax_code": "",
            "local_tax_amt": Decimal("0"),
            "local_tax_percent": Decimal("0"),
            "local2_tax_flag": "N",
            "local2_tax_code": "",
            "local2_tax_amt": Decimal("0"),
            "local2_tax_percent": Decimal("0"),
            "sales_date": sales_date,
            "extended_sales_amt": extended_sales_amt,
            "gift_certificate_num": gift_certificate_num,
            "shipment_num": shipment_num,
            "associate": "77",
            "sales_type": sales_type
        }
        ward_rows.append(ward_row)

    return ward_rows