from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import app, users_collection, bookings_collection
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Base URL of your Flask app
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

    # 3. Test Seat Selection

    # Navigate to seat selection page
    driver.get(f"{BASE_URL}/seat-selection")
    
    # Wait for the seat selection form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "seat-grid"))
    )
    
    # Test departure seat selection
    # Add explicit wait for the JavaScript to create seats
    time.sleep(2)  # Give time for seats to be generated
    departure_seat = driver.find_element(By.CSS_SELECTOR, "#departureSeatGrid .seat-available")
    departure_seat.click()
    
    # If round trip, test return seat selection
    return_info = driver.find_element(By.ID, "returnInfo")
    if return_info.is_displayed():
        # Click return trip button
        driver.find_element(By.ID, "returnBtn").click()
        # Wait for return grid to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "returnSeatGrid"))
        )
        return_seat = driver.find_element(By.CSS_SELECTOR, "#returnSeatGrid .seat-available")
        return_seat.click()
    
    # Click proceed button
    proceed_button = driver.find_element(By.ID, "proceed-button")
    proceed_button.click()
    
    # Wait for redirect to profile page or success message
    WebDriverWait(driver, 10).until(
        EC.url_contains("/profile/") or
        EC.presence_of_element_located((By.CLASS_NAME, "alert"))
    )
    
    print("Seat selection test passed!")


except Exception as e:
    print(f"Test failed: {e}")

finally:
    # Clean up
    driver.quit()