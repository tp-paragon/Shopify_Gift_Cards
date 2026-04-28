from ftplib import FTP
from io import BytesIO
import os
from typing import List

import pandas as pd

def save_csv_file_on_ftp(file_name: str, file_rows: List[dict], dt_stamp: str) -> None:
    FTP_HOST = "paragon.hostedftp.com"
    FTP_USERNAME = os.getenv("FTP_USER", "Value Not Found")
    FTP_PASSWORD = os.getenv("FTP_PASS", "Value Not Found")
    if FTP_USERNAME == "Value Not Found" or FTP_PASSWORD == "Value Not Found":
        print("FTP Credentials not found!", flush=True)
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USERNAME, FTP_PASSWORD)

    df = pd.DataFrame(file_rows)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, header=False)
    csv_buffer.seek(0)
    ftp.storbinary(f"STOR /Shopify/PICKUP/{file_name.upper()}.csv", csv_buffer)
    csv_buffer.seek(0)
    ftp.storbinary(f"STOR /Shopify/Backup/{file_name}/{file_name.upper()} {dt_stamp}.csv", csv_buffer)
    ftp.quit()
    df.to_csv(f"./Output/{file_name.upper()}CSV {dt_stamp}.csv", index=False, header=True)