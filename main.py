from datetime import datetime, timezone, timedelta

from Cloud_Object_Storage.handle_cloud_objects import get_stored_json_data
from Hosted_FTP.handle_ftp_files import save_csv_file_on_ftp
from Utilities.get_orders_to_process import get_orders_to_process
from Utilities.get_processed_line_items import get_processed_line_items
from Utilities.build_gift_card_sale_rows import build_gift_card_sale_rows

GIFT_CARD_SKUS_FILE = "gift_card_skus.json"
gift_card_sale_rows = []

gift_card_skus = set(get_stored_json_data(GIFT_CARD_SKUS_FILE))
print(f"Gift Card Skus Loaded: {len(gift_card_skus)}", flush=True)

utc_now = datetime.now(timezone.utc)
utc_now_str = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
utc_start = utc_now - timedelta(minutes=31)
utc_lookup_str = utc_start.strftime("%Y-%m-%dT%H:%M:%SZ")
print(f"Gift Card Activation Search - From UTC {utc_lookup_str} to {utc_now_str}", flush=True)
orders = get_orders_to_process(utc_lookup_str)
print(f"{len(orders)} Orders to Process...", flush=True)

for order in orders:
    order_id, order_num, created_at = order
    processed_line_items = get_processed_line_items(order_id, "processed_sale_line_items")
    order_gc_rows = build_gift_card_sale_rows(order_id, processed_line_items, gift_card_skus)
    if order_gc_rows:
        gift_card_sale_rows.append(order_gc_rows)
print(f"{len(gift_card_sale_rows)} Gift Card Rows Created", flush=True)

if gift_card_sale_rows:
    save_csv_file_on_ftp("giftcard", gift_card_sale_rows, utc_now_str)
print("~~~ Shopify Intraday Gift Card File Creation Complete ~~~", flush=True)