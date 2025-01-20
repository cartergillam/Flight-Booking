from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import app, users_collection, bookings_collection

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

    # 3. Test Profile Management
    # Navigate to profile page
    driver.get(f"{BASE_URL}/profile/{test_user['email']}")
    
    # Wait for the profile form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "firstName"))
    )
    
    # Test updating profile information
    new_user_data = {
        "firstName": "Johnny",
        "lastName": "Smith",
        "email": "johnnysmith@example.com",
        "password": "newpassword123",
        "confirmPass": "newpassword123"
    }
    
    # Fill out the profile update form
    driver.find_element(By.NAME, "firstName").clear()
    driver.find_element(By.NAME, "firstName").send_keys(new_user_data["firstName"])
    driver.find_element(By.NAME, "lastName").clear()
    driver.find_element(By.NAME, "lastName").send_keys(new_user_data["lastName"])
    driver.find_element(By.NAME, "email").clear()
    driver.find_element(By.NAME, "email").send_keys(new_user_data["email"])
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(new_user_data["password"])
    driver.find_element(By.NAME, "confirmPass").clear()
    driver.find_element(By.NAME, "confirmPass").send_keys(new_user_data["confirmPass"])
    
    # Click Save Changes button
    save_button = driver.find_element(By.XPATH, "//button[@value='Save Changes']")
    save_button.click()
    
    # Wait for profile update to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "firstName"))
    )
    
    # Verify the changes
    updated_first_name = driver.find_element(By.NAME, "firstName").get_attribute("value")
    updated_email = driver.find_element(By.NAME, "email").get_attribute("value")
    assert updated_first_name == new_user_data["firstName"]
    assert updated_email == new_user_data["email"]
    
    print("Profile management test passed!")

except Exception as e:
    print(f"Test failed: {e}")
finally:
    # Clean up
    driver.quit()