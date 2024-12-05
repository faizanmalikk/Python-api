from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Initialize Flask app
app = Flask(__name__)

# Add a basic welcome page
@app.route('/')
def home():
    return "Welcome to the Shipping Calculator API! Use the /calculate_shipping endpoint to calculate shipping."

@app.route('/calculate_shipping', methods=['POST'])
def calculate_shipping():
    try:
        # Extract input from the request
        data = request.get_json()
        from_zip = data.get('from_zip')
        to_zip = data.get('to_zip')
        weight = data.get('weight')

        # Print inputs for debugging
        print(f"Received data - from_zip: {from_zip}, to_zip: {to_zip}, weight: {weight}")

        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Uncomment the following line to run in headless mode
        chrome_options.add_argument("--headless")

        # Initialize the Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open the SpeedeeDelivery shipping calculator page
        driver.get("https://speedeedelivery.com/services/shipping-calculator/")

        # Input data into the form fields
        from_zip_input = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/div[2]/form/table/tbody/tr[1]/td[1]/input")
        from_zip_input.send_keys(from_zip)

        to_zip_input = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/div[2]/form/table/tbody/tr[1]/td[2]/input")
        to_zip_input.send_keys(to_zip)

        weight_input = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/div[2]/form/table/tbody/tr[1]/td[3]/input")
        weight_input.send_keys(weight)

        # Submit the form
        weight_input.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(5)  # Adjust this as necessary based on page load time

        # Scrape the table data
        table = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/div[3]/table")
        table_data = table.text

        # Scrape the image
        image = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/div[3]/div[1]/img")
        image_src = image.get_attribute("src")

        # Close the driver
        driver.quit()

        # Return the results as JSON
        return jsonify({"table_data": table_data, "image_url": image_src})

    except Exception as e:
        # Print the error for debugging
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
