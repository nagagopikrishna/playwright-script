import json
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = 'session.json'
LOGIN_URL = "https://hiring.idenhq.com/challenge"
USERNAME = "your_email@example.com"
PASSWORD = "your_password"

# Load or save session
def load_session(context):
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as file:
            storage_state = json.load(file)
        context.add_cookies(storage_state['cookies'])


def save_session(context):
    storage = context.cookies()
    with open(SESSION_FILE, 'w') as file:
        json.dump({"cookies": storage}, file)


# Function to log in
def login(page):
    page.goto(LOGIN_URL)
    page.fill('input[type="email"]', USERNAME)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_selector("text=Product Dashboard")


# Navigate to the hidden product table
def navigate_to_products(page):
    # Example steps — adapt as needed
    page.click('text=Instructions')
    page.click('text=Product Dashboard')
    page.wait_for_selector("text=Product Inventory")


# Extract product data, handling pagination
def extract_products(page):
    products = []
    while True:
        rows = page.locator('.product-card').all()
        for row in rows:
            product = {
                "name": row.locator("h4").inner_text(),
                "id": row.locator("text=ID:").nth(0).inner_text().split()[-1],
                "warranty": row.locator("text=Warranty").nth(0).inner_text().split()[-1],
                "manufacturer": row.locator("text=Manufacturer").nth(0).inner_text().split()[-1],
                "color": row.locator("text=Color").nth(0).inner_text().split()[-1]
            }
            products.append(product)

        # Check for next page button
        next_button = page.locator('button[aria-label="Next"]')
        if next_button.is_enabled():
            next_button.click()
            page.wait_for_timeout(1000)
        else:
            break

    return products


# Save data to JSON
def save_to_json(data):
    with open('product_data.json', 'w') as file:
        json.dump(data, file, indent=4)


# Main script
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    load_session(context)

    page = context.new_page()
    page.goto(LOGIN_URL)

    # If not logged in, perform login
    if not page.is_visible("text=Product Dashboard"):
        login(page)
        save_session(context)

    navigate_to_products(page)


    product_data = extract_products(page)

    save_to_json(product_data)

    print("✅ Product data extraction completed!")
    browser.close()
