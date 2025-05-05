# To make sure all dependencies are installed, run:
# pip install pandas openpyxl --break-system-packages

import os
import subprocess
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse

def sanitize_target(raw):
    raw = raw.strip()
    if not raw:
        return None

    parsed = urlparse(raw if raw.startswith("http") else "http://" + raw)
    hostname = parsed.hostname or raw

    # Remove common subdomain prefixes
    if hostname.startswith(("www.", "ftp.", "mail.", "news.")):
        hostname = ".".join(hostname.split(".")[1:])

    return hostname.lower()

def extract_whois_data(raw_text):
    lines = raw_text.splitlines()
    data = {
        "Domain Name": "",
        "Registration Date": "",
        "Expiration Date": "",
        "Name Servers": []
    }

    for line in lines:
        line_lower = line.lower()
        if "domain name:" in line_lower and not data["Domain Name"]:
            data["Domain Name"] = line.split(":")[-1].strip()
        elif "creation date:" in line_lower and not data["Registration Date"]:
            data["Registration Date"] = line.split(":")[-1].strip()
        elif "registry expiry date:" in line_lower and not data["Expiration Date"]:
            data["Expiration Date"] = line.split(":")[-1].strip()
        elif "name server:" in line_lower:
            ns = line.split(":")[-1].strip()
            if ns and ns not in data["Name Servers"]:
                data["Name Servers"].append(ns)

    return data

def prompt_for_file():
    while True:
        file_path = input("Enter the path to your .txt file with targets: ").strip()
        if os.path.isfile(file_path):
            return file_path
        print("Invalid file path. Please try again.")

def main():
    project_name = input("Enter the Project Name: ").strip()
    input_file = prompt_for_file()

    today = datetime.now().strftime("%m.%d")
    output_dir = f"{project_name}_Whois"
    full_results_dir = os.path.join(output_dir, "Full Whois Results")
    os.makedirs(full_results_dir, exist_ok=True)

    spreadsheet_path = os.path.join(output_dir, f"{project_name}_Whois_Results.xlsx")

    with open(input_file, "r") as f:
        raw_targets = sorted(set([line.strip() for line in f if line.strip()]))

    print(f"Running whois for {len(raw_targets)} targets...")
    result_rows = []

    for idx, raw_target in enumerate(raw_targets, 1):
        sanitized_target = sanitize_target(raw_target)
        print(f"[{idx}/{len(raw_targets)}] {sanitized_target}")

        if not sanitized_target:
            print("  ❌ Skipping invalid target.")
            continue

        filename = f"{sanitized_target.replace('/', '_')}.txt"
        txt_path = os.path.join(full_results_dir, filename)

        try:
            result = subprocess.check_output(["whois", sanitized_target], stderr=subprocess.STDOUT, text=True, timeout=15)
            with open(txt_path, "w") as out_file:
                out_file.write(result)
            parsed = extract_whois_data(result)

            result_rows.append({
                "Target": sanitized_target,
                "Domain Name": parsed["Domain Name"] or "No WHOIS info found",
                "Registration Date": parsed["Registration Date"],
                "Expiration Date": parsed["Expiration Date"],
                "Name Servers": "\n".join(parsed["Name Servers"]),
                "Full Results": txt_path
            })

        except subprocess.TimeoutExpired:
            message = "WHOIS lookup timed out."
            print(f"  ⚠️ {message}")
            with open(txt_path, "w") as out_file:
                out_file.write(message)
            result_rows.append({
                "Target": sanitized_target,
                "Domain Name": message,
                "Registration Date": "",
                "Expiration Date": "",
                "Name Servers": "",
                "Full Results": txt_path
            })
        except subprocess.CalledProcessError as e:
            message = "WHOIS lookup failed or not in database."
            print(f"  ⚠️ {message}")
            with open(txt_path, "w") as out_file:
                out_file.write(e.output or message)
            result_rows.append({
                "Target": sanitized_target,
                "Domain Name": message,
                "Registration Date": "",
                "Expiration Date": "",
                "Name Servers": "",
                "Full Results": txt_path
            })

    df = pd.DataFrame(result_rows)
    df.to_excel(spreadsheet_path, index=False)

    # Auto-fit column widths and manually set "Name Servers" width
    from openpyxl import load_workbook
    wb = load_workbook(spreadsheet_path)
    ws = wb.active

    for column_cells in ws.columns:
        column = column_cells[0].column_letter
        header = column_cells[0].value
        if header == "Name Servers":
            ws.column_dimensions[column].width = 45
        else:
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column_cells)
            ws.column_dimensions[column].width = max_length + 2

    wb.save(spreadsheet_path)

    print(f"\n✔ All results saved in: {output_dir}")
    print(f"✔ Spreadsheet created at: {spreadsheet_path}")

if __name__ == "__main__":
    main()
