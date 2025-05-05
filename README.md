### 🐍 Python Setup Instructions

To run any of the automation scripts in this project, make sure you have Python 3 installed. Most systems come with Python pre-installed. If not, you can download it here:

➡️ [https://www.python.org/downloads/](https://www.python.org/downloads/)

> ✅ **Recommended:** Use Python 3.9 or newer for compatibility with all libraries used in these scripts.

Once Python is installed, check the comment at the top of the script to see all  required libraries

> 🛠️ If you're running on Kali Linux or a similar distro with protected environments, include the `--break-system-packages` flag when installing libraries.

---

### 📌 Script: `URLChecker.py`

**Description**:  
Reads a list of domain names from a `.txt` file and checks whether each one is accessible via both HTTPS and HTTP. For every domain that responds successfully, it opens the page in a Firefox browser window and captures a screenshot of just the webpage.

The browser is automatically resized for consistent screenshot dimensions.

**Usage:**
1. Install dependencies:
   ```bash
   pip install requests selenium webdriver-manager
   sudo apt install scrot
   ```
2. Run the script using:
   ```bash
   python URLChecker.py
   ```
3. You'll be prompted to enter:
   - A project name.
   - The path to the `.txt` file containing your URLs.

**Output**:
   - A folder named `<ProjectName>_URLCheck (MM.DD)` will be created.
   - For each accessible domain, a screenshot will be saved as `<domain>.png`.
   - An `Accessibility.txt` log file will summarize the HTTP/HTTPS results per domain.

---

### 📌 Script: `Whoiser.py`

**Description:**  
Automates WHOIS lookups on a list of domains and compiles the parsed results into a formatted spreadsheet. For each target, it extracts the domain name, registration and expiration dates, name servers, and saves the raw WHOIS output in a text file.

**Usage:**

1. Install dependencies:
   ```bash
   pip install pandas openpyxl
   ```

2. Run the script:
   ```bash
   python Whoiser.py
   ```

3. You'll be prompted to enter:
   - A project name.
   - The path to the `.txt` file containing your URLs.


The script will:
   - Sanitize and deduplicate targets
   - Run WHOIS lookups
   - Save full WHOIS results to a text file per domain
   - Generate a spreadsheet `<ProjectName>_Whois_Results.xlsx` inside a folder called `<ProjectName>_Whois`

**Output**
- A folder named `<ProjectName> Whois` will be created.
- For each accessible domain, the Whois results will be saved as `<domain>.txt`.
- The spreadsheet will contain:
   - `Target`: The sanitized domain input.
   - `Domain Name`: The official domain name from WHOIS.
   - `Registration Date`: When the domain was created.
   - `Expiration Date`: When the domain is set to expire.
   - `Name Servers`: Line-separated list of name servers.
   - `Full Results`: Path to the full WHOIS text file.

**Output Directory Structure:**
```
<ProjectName> Whois/
├── Full Whois Results/
│   ├── example.com.txt
│   ├── ...
└── <ProjectName>_Whois_Results.xlsx
```

---

### 📌 Script: `DNSReconner.py`

Automate the running and screenshotting of DNSrecon results
W.I.P.

---

### 📌 Script: `WafW00fer.py`

Automate the running and screenshotting of WafW00f results
W.I.P.

---

### 📌 Script: `Curler.py`

Automate the running and screenshotting of Curl results
W.I.P.

---

### 📌 Script: `Sublisterer.py`

Automate the running and screenshotting of Sublister results, compile important data into a spreadsheet
W.I.P.

---

### 📌 Script: `Harvesterer.py`

Automate the running and screenshotting of TheHarvester results, compile important data into a spreadsheet
W.I.P.

---

### 📌 Script: `Niktoer.py`

Automate the running and screenshotting of Nikto results
W.I.P.

---

### 📌 Script: `NMaper.py`

(VA) Automate the running and screenshotting of NMap results, parse through results for all open ports, compile data in .txt file
W.I.P.

---

### 📌 Script: `Clickjacker.py`

**Description:**
This script automates the detection of potential **clickjacking vulnerabilities** across a list of web targets. It leverages `requests` for HTTP header analysis, `selenium` and `pyautogui` for browser automation and layout management, and `pandas` + `openpyxl` for result recording in a spreadsheet.

**Usage:**

1. Install dependencies:
   ```bash
   pip install requests selenium pandas pyautogui beautifulsoup4 openpyxl
   ```
2. Run the script:
   ```bash
   python Clickjacker.py
   ```
   
3. You'll be prompted to enter:
   - A project name.
   - The path to the `.txt` file containing your URLs.

The script will:
   - Launch Firefox and snap the window to the **left half** of the screen
   - Open Mousepad a test HTML file and snaps to the **right half**
   For each target:
   - Retrieves IP address and HTTP headers using `requests`
   - Checks for `X-Frame-Options` and `Content-Security-Policy (frame-ancestors)`
   - Creates an HTML file embedding the target in an iframe to simulate clickjacking
   - Displays both the test page and HTML content side-by-side
   - Takes a screenshot of the result with `pyautogui`
   - Deletes the temporary HTML file after the check
   - Kills Mousepad after viewing

**Output:**
- A folder named `{ProjectName}_Clickjacking`
- Inside it:
  - One `.xlsx` spreadsheet including headers, time accessed
  - One screenshot per target showing iframe rendering status
