from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import app, users_collection, bookings_collection
import time
import os

# This code is only needed if webdriver is already installed on the system
'''
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
'''

# Set up the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL of Flask app
BASE_URL = "http://127.0.0.1:5000"

# Test data for registration and login
test_user = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "johndoe@example.com",
    "password": "password123",
    "confirmPass": "password123"
}

# Function to clear the MongoDB database before running the tests
def clear_mongodb_database():
    # Clear the relevant collections
    users_collection.delete_many({})
    bookings_collection.delete_many({})
    print("MongoDB database cleared!")

clear_mongodb_database()

try:
    # 1. Test Registration
    driver.get(f"{BASE_URL}/register")

    # Fill out the registration form
    driver.find_element(By.NAME, "firstName").send_keys(test_user["firstName"])
    driver.find_element(By.NAME, "lastName").send_keys(test_user["lastName"])
    driver.find_element(By.NAME, "email").send_keys(test_user["email"])
    driver.find_element(By.NAME, "password").send_keys(test_user["password"])
    driver.find_element(By.NAME, "confirmPass").send_keys(test_user["confirmPass"])
    
    # Submit the form
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    
    # Wait and verify redirection to login page
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))
    print("Registration test passed!")

    # 2. Test Login
    driver.get(f"{BASE_URL}/login")

    # Fill out the login form
    driver.find_element(By.NAME, "email").send_keys(test_user["email"])
    driver.find_element(By.NAME, "password").send_keys(test_user["password"])
    
    # Submit the form
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    
    # Wait and verify redirection to flightSearch page
    WebDriverWait(driver, 10).until(EC.url_contains("/"))
    print("Login test passed!")

    # Add a booking for the test user
    booking = {
        "user_email": test_user["email"],
        "departureSeat": "12A",
        "returnSeat": "14B",
        "trip_type": "round_trip",
        "to_city": "CityA",
        "from_city": "CityB"
    }
    bookings_collection.insert_one(booking)
    print("Test booking added!")

    # 3. Test Booking History
    driver.get(f"{BASE_URL}/booking-history")

    # Wait for the booking history page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "container")))

    # Verify the booking history content
    assert "Booking History" in driver.page_source
    print("Booking history test passed!")

except Exception as e:
    print(f"Test failed: {e}")

finally:
    # Clean up
    driver.quit()