# To make sure all dependencies are installed, run:
# pip install requests selenium webdriver-manager --break-system-packages
# sudo apt install scrot

import os
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

def get_screenshot(url, driver, folder_path):
    try:
        driver.get(url)
        time.sleep(3)  # Let page and UI load

        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        screenshot_path = os.path.join(folder_path, f"{safe_name}.png")
        driver.save_screenshot(screenshot_path)
    except Exception as e:
        print(f"Failed to take screenshot for {url}: {e}")

def sanitize_url(url):
    return url.replace("https://", "").replace("http://", "").strip("/")

def prompt_for_file():
    while True:
        file_path = input("Enter the path to your .txt file with URLs: ").strip()
        if os.path.isfile(file_path):
            return file_path
        print("Invalid file path. Please try again.")

def main():
    project_name = input("Enter the Project Name: ").strip()
    input_file = prompt_for_file()

    today = datetime.now().strftime("%m.%d")
    output_dir = f"{project_name} URLCheck ({today})"
    os.makedirs(output_dir, exist_ok=True)
    
    access_log_path = os.path.join(output_dir, f"{project_name}_Accessibility.txt")

    with open(input_file, "r") as f:
        raw_urls = sorted(set([line.strip() for line in f if line.strip()]))

    total = len(raw_urls)
    print(f"\nTesting {total} URLs...\n")

    options = Options()
    options.headless = False
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )
    driver.set_window_size(1280, 900)
    time.sleep(1)

    with open(access_log_path, "w") as log_file:
        try:
            for idx, raw_url in enumerate(raw_urls, 1):
                sanitized = sanitize_url(raw_url)
                print(f"[{idx}/{total}] Testing {sanitized}...")

                https_url = f"https://{sanitized}"
                http_url = f"http://{sanitized}"
                status_https = status_http = False

                screenshot_taken = False
                screenshot_url = None

                # Try HTTPS
                try:
                    response = requests.get(https_url, timeout=5, allow_redirects=True, stream=True, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
                    })
                    if response.status_code < 400:
                        status_https = True
                        print("✓ HTTPS", end=" ")
                        screenshot_url = https_url
                    else:
                        print("✗ HTTPS (status)", end=" ")
                except:
                    print("✗ HTTPS (fail)", end=" ")

                # Try HTTP
                try:
                    response = requests.get(http_url, timeout=5, allow_redirects=True, stream=True, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
                    })
                    if response.status_code < 400:
                        status_http = True
                        print("✓ HTTP", end=" ")
                        if not screenshot_url:
                            screenshot_url = http_url
                    else:
                        print("✗ HTTP (status)", end=" ")
                except:
                    print("✗ HTTP (fail)", end=" ")

                # Screenshot priority: HTTPS > HTTP
                if screenshot_url:
                    get_screenshot(screenshot_url, driver, output_dir)
                    print("| Screenshot taken")
                else:
                    print("| No screenshot")

                # Write to log
                log_file.write(f"{sanitized}\n")
                log_file.write(f"{'✓' if status_https else '✗'} https  {'✓' if status_http else '✗'} http\n\n")

        finally:
            driver.quit()
            print(f"\nAccessibility log saved at: {access_log_path}")

if __name__ == "__main__":
    main()
