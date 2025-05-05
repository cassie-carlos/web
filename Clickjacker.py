# To make sure all dependencies are installed, run:
# pip install requests selenium pandas pyautogui beautifulsoup4 openpyxl

import os
import time
import socket
import requests
import pyautogui
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import subprocess
from openpyxl import load_workbook

# === Get input from user ===
project_name = input("Enter the Project Name: ")
while True:
    input_file = input("Enter the path to your .txt file with URLs: ")
    if not os.path.isfile(input_file):
        print(f"[!] File '{input_file}' does not exist. Please try again.")
        continue
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        print(f"[!] File '{input_file}' is empty or has no valid targets. Please try again.")
    else:
        break
task_name = "Clickjacking"
output_dir = f"{project_name}_{task_name}"
os.makedirs(output_dir, exist_ok=True)

# === Set up Firefox browser ===
firefox_options = Options()
firefox_options.add_argument("--width=960")
firefox_options.add_argument("--height=1080")
driver = webdriver.Firefox(options=firefox_options)
driver.set_window_position(0, 0)

# === Read targets ===
with open(input_file, 'r') as f:
    targets = [line.strip() for line in f if line.strip()]

results = []

for idx, url in enumerate(targets, 1):
    if not url.startswith("http"):
        url = "http://" + url

    print(f"[{idx}/{len(targets)}] Testing {url}...")

    try:
        domain = url.split("//")[-1].split("/")[0]
        ip_address = socket.gethostbyname(domain)
    except Exception:
        ip_address = "N/A"

    accessed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        xfo = headers.get("X-Frame-Options", "Not Present")
        csp = headers.get("Content-Security-Policy", "Not Present")

        # Parse CSP for frame-ancestors
        frame_ancestors = "Not Present"
        if "frame-ancestors" in csp:
            for part in csp.split(";"):
                if "frame-ancestors" in part:
                    frame_ancestors = part.strip()
                    break

        raw_headers = "\n".join(f"{k}: {v}" for k, v in headers.items())

    except Exception as e:
        xfo = csp = raw_headers = "Request Failed"
        frame_ancestors = "Not Present"

    # === Create iframe test page ===
    test_html = f"""<html>
    <head><title>Clickjack test page</title></head>
    <body>
        <iframe src="{url}" width="500" height="500"></iframe>
    </body>
</html>"""

    html_path = os.path.join(output_dir, f"{domain}_clickjack_test.html")
    with open(html_path, 'w') as f:
        f.write(test_html)

    # === Open in Mousepad (right side) ===
    subprocess.Popen(["mousepad", html_path])
    time.sleep(1)
    pyautogui.hotkey("win", "right")  # snap mousepad to right
    time.sleep(1)

    # === Open HTML in Firefox (left side) ===
    driver.get("file://" + os.path.abspath(html_path))
    time.sleep(3)

    # === Determine vulnerability ===
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    iframe = soup.find("iframe")
    vulnerable = "Yes" if iframe and iframe.get("src") else "No"

    # === Screenshot ===
    screenshot_name = os.path.join(output_dir, f"{domain}_screenshot.png")
    pyautogui.screenshot(screenshot_name)

    # === Record result ===
    results.append({
        "Target": url,
        "IP Address": ip_address,
        "Time (accessed)": accessed_time,
        "X-Frame-Options": xfo,
        "CSP Header (Frame-Ancestors)": frame_ancestors,
        "Raw HTTP Headers": raw_headers
    })

    subprocess.call(["pkill", "mousepad"])  # close mousepad

    # === Delete the temporary HTML file ===
    try:
        os.remove(html_path)
    except Exception as e:
        print(f"[!] Failed to delete {html_path}: {e}")

# === Close browser ===
driver.quit()

# === Save results to spreadsheet ===
df = pd.DataFrame(results)
spreadsheet_path = os.path.join(output_dir, f"{project_name}_HTTP-Headers.xlsx")
df.to_excel(spreadsheet_path, index=False)

# === Auto-fit column widths ===
wb = load_workbook(spreadsheet_path)
ws = wb.active

for column_cells in ws.columns:
    column = column_cells[0].column_letter
    header = column_cells[0].value
    if header == "Raw HTTP Headers":
        ws.column_dimensions[column].width = 60
    else:
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column_cells)
        ws.column_dimensions[column].width = max_length + 2

wb.save(spreadsheet_path)

print(f"\nScan complete. Results saved to: {spreadsheet_path}")
