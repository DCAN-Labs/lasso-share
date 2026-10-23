#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LORIS CRF CSV Batch Downloader
Loops through a range of CRF IDs and downloads each CSV file.
"""

import os
import time
import getpass
import requests
from bs4 import BeautifulSoup

# ==========================================
# --- CONFIGURATION ---
# ==========================================
BASE_URL = "https://prod.hbcd.msi.umn.edu"
LOGIN_URL = f"{BASE_URL}/index.php"
OUTPUT_DIR = "./loris_crf_csvs"

# Define start and end IDs (inclusive)
START_ID = 100
END_ID = 110

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# --- STEP 1: AUTHENTICATION ---
# ==========================================
def login():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    print("=== LORIS Authentication ===")
    username = input("Enter LORIS Username: ").strip()
    password = getpass.getpass("Enter LORIS Password: ")

    try:
        # Check login page for potential CSRF token
        login_page = session.get(BASE_URL, timeout=15)
        soup = BeautifulSoup(login_page.text, "html.parser")
        
        csrf_input = (
            soup.find("input", {"name": "csrf_token"}) or 
            soup.find("input", {"name": "csrf"})
        )
        
        payload = {
            "username": username,
            "password": password,
            "login": "Log In"
        }
        if csrf_input and csrf_input.get("value"):
            payload["csrf_token"] = csrf_input["value"]

        res = session.post(LOGIN_URL, data=payload, timeout=15)
        
        if "login" in res.url.lower() and "logout" not in res.text.lower():
            print("[!] Login failed. Please check your credentials.")
            return None
        
        print("[+] Logged in successfully!\n")
        return session

    except Exception as e:
        print(f"[-] Authentication error: {e}")
        return None

# ==========================================
# --- STEP 2: LOOP & DOWNLOAD CSVs ---
# ==========================================
def download_crf_range(session, start_id, end_id):
    # range(start_id, end_id + 1) ensures end_id (110) is included
    id_range = range(start_id, end_id + 1)
    downloaded_count = 0

    print(f"[*] Starting download for CRF IDs {start_id} through {end_id}...\n")

    for crf_id in id_range:
        url = f"{BASE_URL}/imaging_browser/crf/{crf_id}"
        filepath = os.path.join(OUTPUT_DIR, f"crf_{crf_id}.csv")

        print(f"[*] Fetching CRF #{crf_id}: {url}")
        
        try:
            response = session.get(url, timeout=15)

            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                
                # Verify we received actual file content rather than an HTML error/login redirect
                if "text/html" in content_type.lower() and "<html" in response.text.lower():
                    print(f"    [!] ID {crf_id} returned HTML page instead of CSV (likely invalid ID or missing permissions).")
                else:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    print(f"    [+] Saved -> {filepath}")
                    downloaded_count += 1
            else:
                print(f"    [!] Failed to download ID {crf_id}. HTTP Status: {response.status_code}")

        except Exception as e:
            print(f"    [-] Error downloading ID {crf_id}: {e}")

        # Politeness delay between requests
        time.sleep(0.5)

    print(f"\n[+] Task finished! Successfully downloaded {downloaded_count} CSV file(s) to '{OUTPUT_DIR}'.")

# ==========================================
# --- MAIN EXECUTION ---
# ==========================================
if __name__ == "__main__":
    session = login()
    if session:
        download_crf_range(session, START_ID, END_ID)