import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def setup_driver():
    """Sets up Selenium WebDriver with Firefox."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set Firefox binary location manually (if needed)
    options.binary_location = "/usr/bin/firefox"  # Change this if necessary

    # Use GeckoDriver for Firefox
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver

# Function to open the IBM lifecycle page
def open_ibm_lifecycle_page(driver):
    url = "https://www.ibm.com/support/pages/lifecycle/"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Function to search for the software
def search_product(driver, product_name):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "plc--query"))
        )
        search_box.clear()
        search_box.send_keys(product_name)

        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='button' and @value='Search']"))
        )
        driver.execute_script("arguments[0].click();", search_button)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "plc--results-table"))
        )
    except Exception as e:
        return f"Error searching for {product_name}: {e}"

# Function to extract EOL date
def extract_eol_date(driver, product_name, version):
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "plc--results-table"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 5:
                software_name = cols[1].text.strip().lower()
                software_version = cols[2].text.strip()

                if product_name.lower() in software_name and version in software_version:
                    eol_date = cols[6].text.strip()
                    return f"🟢 EOL Date for {product_name} {version}: {eol_date}"

        return "🔴 Software/version not found in search results."
    except Exception as e:
        return f"❌ Error extracting EOL date: {e}"

# Streamlit UI
st.title("IBM Software Lifecycle EOL Date Finder")
st.write("Enter the software name and version to find its end-of-life (EOL) date.")

product_name = st.text_input("Software Name", value="IBM WebSphere")
version = st.text_input("Version", value="9.0")

if st.button("Search"):
    st.write("🔍 Searching for EOL Date...")
    driver = setup_driver()
    try:
        open_ibm_lifecycle_page(driver)
        search_product(driver, product_name)
        result = extract_eol_date(driver, product_name, version)
        st.success(result)
    finally:
        driver.quit()
