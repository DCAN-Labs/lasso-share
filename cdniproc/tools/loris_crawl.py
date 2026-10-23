#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 14:27:30 2026

@author: kweldon
"""

# import os
# import time
# from urllib.parse import urljoin, urlparse
# import requests
# from bs4 import BeautifulSoup


# # --- CONFIGURATION ---
# BASE_URL = "https://prod.hbcd.msi.umn.edu"
# LOGIN_URL = f"{BASE_URL}/index.php"  # Standard LORIS login form target
# TARGET_URL = "https://prod.hbcd.msi.umn.edu/imaging_browser/?brain_rating=Abnormal+brain" # Starting point for crawling
# OUTPUT_DIR = "./loris_html_downloads"

# # LORIS User Credentials
# USERNAME = "kweldon@umn.edu"
# PASSWORD = "Mynewpassword345"

# # List of CandIDs, Visit Labels, and Instrument Names to download
# # Adjust URL patterns to match your target forms/pages in LORIS
# TARGET_PARAMS = [
#     {"instrument": "CRF Reports"}
# ]

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # --- 1. SESSION AUTHENTICATION ---
# session = requests.Session()

# # Fetch login page to capture any CSRF token if required
# login_page = session.get(BASE_URL)
# soup = BeautifulSoup(login_page.text, 'html.parser')

# payload = {
#     'username': USERNAME,
#     'password': PASSWORD,
#     'login': 'Log In'
# }

# # Submit authentication request
# response = session.post(LOGIN_URL, data=payload)

# if "logout" not in response.text.lower() and response.status_code == 200:
#     print("[!] Login failed. Please check your credentials or LORIS login endpoint.")
#     exit()

# print("[+] Successfully logged into LORIS.")


# --- CONFIGURATION ---
import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BASE_URL = "https://prod.hbcd.msi.umn.edu"
#BASE_URL = "https://prod.hbcd.msi.umn.edu/imaging_browser/"
LOGIN_URL = f"{BASE_URL}/index.php"  # Standard LORIS authentication handler
FILTER_URL = f"{BASE_URL}/imaging_browser/?brain_rating=Abnormal+brain"
#FILTER_URL = f"{BASE_URL}/?brain_rating=Abnormal+brain"
OUTPUT_DIR = "./hbcd_abnormal_brain_html"

# Credentials
USERNAME = "umn.edu"
PASSWORD = "pass"

os.makedirs(OUTPUT_DIR, exist_ok=True)
session = requests.Session()

# Add a browser User-Agent so the request isn't blocked as a bot
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

# --- STEP 1: INITIAL VISIT & CSRF TOKEN FETCH ---
print("[*] Connecting to LORIS login page...")
initial_res = session.get(BASE_URL)
soup_login = BeautifulSoup(initial_res.text, "html.parser")

# Check if LORIS uses a CSRF token in the login form
csrf_token = None
csrf_input = soup_login.find("input", {"name": "csrf_token"}) or soup_login.find("input", {"name": "csrf"})
if csrf_input and csrf_input.get("value"):
    csrf_token = csrf_input["value"]
    print(f"[+] Captured CSRF token: {csrf_token[:10]}...")

# --- STEP 2: SUBMIT LOGIN CREDENTIALS ---
payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "login": "Log In"
}
if csrf_token:
    payload["csrf_token"] = csrf_token

print(f"[*] Submitting authentication to {LOGIN_URL}...")
login_res = session.post(LOGIN_URL, data=payload)

# Verify if login succeeded
# (LORIS sets session cookies on successful auth and removes the login form)
if "login" in login_res.url.lower() and "logout" not in login_res.text.lower():
    print("\n[!] Login failed. Please check your username/password.")
    print("Note: If UMN uses MKey / Single Sign-On (SSO), programmatic login will fail, and session cookie injection must be used instead.")
    exit()

print("[+] Authenticated successfully!")

# --- STEP 3: ACCESS FILTERED VIEW & COLLECT LINKS ---
print(f"[*] Accessing target URL: {FILTER_URL}")
filter_res = session.get(FILTER_URL)

# Save the main table/filter index page
index_path = os.path.join(OUTPUT_DIR, "index_abnormal_brain.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(filter_res.text)
print(f"[] Saved index page to {index_path}")

# Parse for individual scan links
soup_filter = BeautifulSoup(filter_res.text, "html.parser")
target_links = set()

for a_tag in soup_filter.find_all("a", href=True):
    href = a_tag["href"]
    # Collect links leading to specific scan/candidate detail pages
    if "" in href and any(param in href for param in ["imaging_browser_view_allsites"]):
        full_url = urllib.parse.urljoin(BASE_URL, href)
        target_links.add(full_url)

print(f"[+] Discovered {len(target_links)} detail pages to download.\n")

response = session.get(FILTER_URL)
print(f"Status Code: {response.status_code}")
print(f"Page Title: {BeautifulSoup(response.text, 'html.parser').title}")
print(f"Found <a> tags: {len(BeautifulSoup(response.text, 'html.parser').find_all('a'))}")

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Perform fetch on target URL using your active session
response = session.get(FILTER_URL)
soup = BeautifulSoup(response.text, 'html.parser')

print("--- LINK INSPECTION ---")
for i, a in enumerate(soup.find_all('a', href=True), 1):
    raw_href = a['href']
    full_url = urljoin(BASE_URL, raw_href)
    
    # Check individual criteria
    parsed = urlparse(full_url)
    base_parsed = urlparse(BASE_URL)
    
    same_domain = parsed.netloc == base_parsed.netloc
    has_fragment = bool(parsed.fragment)
    
    print(f"{i}. Href: {raw_href}")
    print(f"   Full URL: {full_url}")
    print(f"   Same Domain: {same_domain} | Has #: {has_fragment}")
    print("-" * 40)

import os
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://prod.hbcd.msi.umn.edu"
TARGET_URL = "https://prod.hbcd.msi.umn.edu/imaging_browser/"
DOWNLOAD_DIR = "./hbcd_pages"
DRY_RUN = True

# Explicitly list modules or allow paths starting with target subroutes
ALLOWED_PREFIXES = ["/imaging_browser", "/candidate_list", "/instruments"]

visited_urls = set()
session = requests.Session()

# Add your auth cookies/headers here
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def is_valid_loris_link(url):
    parsed = urlparse(url)
    base_parsed = urlparse(BASE_URL)
    
    # Must be same domain
    if parsed.netloc != base_parsed.netloc:
        return False
        
    if url in visited_urls:
        return False

    # Check if path starts with one of the target LORIS modules
    path = parsed.path
    return any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)

def sanitize_route_filename(url):
    """Converts dynamic paths like /imaging_browser/?submodule=1 into safe filenames."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    if not path:
        filename = "index"
    else:
        filename = path.replace('/', '_')
        
    if parsed.query:
        filename += "_" + parsed.query.replace('=', '-').replace('&', '_')
        
    filename = "".join([c for c in filename if c.isalnum() or c in ('_', '-')])
    return f"{filename}.html"

def crawl_loris(url):
    if url in visited_urls:
        return
    
    visited_urls.add(url)
    filename = sanitize_route_filename(url)

    if DRY_RUN:
        print(f"[DRY-RUN] Found route: {url}")
        print(f"          Will save as: {filename}")
    else:
        print(f"[+] Downloading: {url}")

    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            return

        if not DRY_RUN:
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all module links
        for a in soup.find_all('a', href=True):
            full_url = urljoin(BASE_URL, a['href'])
            # Clean anchor tags (#)
            clean_url = urlparse(full_url)._replace(fragment="").geturl()
            
            if is_valid_loris_link(clean_url):
                time.sleep(1)
                crawl_loris(clean_url)

    except Exception as e:
        print(f"[-] Error: {e}")

# Run against the imaging browser route
crawl_loris(TARGET_URL)