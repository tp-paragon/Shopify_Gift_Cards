from datetime import datetime
import pytz

def get_date_time(utc_time_str: str) -> tuple:
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_zone = pytz.timezone("UTC")
    est_zone = pytz.timezone("America/New_York")
    utc_time = utc_zone.localize(utc_time)
    est_time = utc_time.astimezone(est_zone)
    time_string = est_time.strftime("%Y%m%d %H%M%S %Z")
    dt, tm, *rest = time_string.split()
    return dt, tm