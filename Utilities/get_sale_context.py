def get_store(order_num: str, app: dict|None, retail_location: dict|None):
    app_id = app.get("id", "") if app else ""
    app_name = app.get("name", "") if app else ""
    location_id = retail_location.get("id", "") if retail_location else ""
    location_name = retail_location.get("name", "") if retail_location else ""
    if app_name in ("Online Store", "Locally Sales Channel"):
        return "3"
    if app_name == "Draft Orders":
        return "7"
    # Expo Location
    if location_id == "gid://shopify/Location/107956109597":
        return "2"
    # Point of Sale App and Union Square Store Location
    if app_id == "gid://shopify/App/129785" and location_id == "gid://shopify/Location/107803672861":
        return "1"
    print(f"Error - Order {order_num} Store 50 Sale | App: {app_id}, {app_name} | Location: {location_id}, {location_name}", flush=True)
    return "50"