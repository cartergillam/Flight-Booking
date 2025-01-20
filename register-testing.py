import unittest
from flask import Flask
from app import app, users_collection  

class RegisterTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()  
        cls.app.testing = True

    # Setup before each test
    def setUp(self):
        # Clear the users collection before each test
        users_collection.delete_many({})

    # Test case where all fields are filled correctly (successful registration)
    def test_successful_registration(self):
        response = self.app.post('/register', data={
            'firstName': 'Kavin',
            'lastName': 'Arasu',
            'email': 'johndoe@gmail.com',
            'password': 'password12',
            'confirmPass': 'password12'
        })
        self.assertEqual(response.status_code, 302)  # Expect 302 for redirection to the login page
        self.assertIsNotNone(users_collection.find_one({"email": 'johndoe@gmail.com'}))  # Ensure the user was added to the MongoDB collection

    # Test case for when passwords do not match
    def test_password_mismatch(self):
        response = self.app.post('/register', data={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'confirmPass': 'password456'
        })
        self.assertEqual(response.status_code, 200)  # Expect 200 OK, meaning it stays on the same page
        self.assertIn(b"Passwords do not match", response.data)  # Check if the error message is in the response

    # Test case for missing fields (empty email)
    def test_missing_field(self):
        response = self.app.post('/register', data={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': '',
            'password': 'password123',
            'confirmPass': 'password123'
        })
        self.assertEqual(response.status_code, 200)  # Expect 200 OK, meaning it stays on the same page
        self.assertIn(b"Fill out all fields", response.data)  # Check if the error message is in the response

    # Test case where the email is already registered
    def test_email_already_registered(self):
        # First, add a user to the MongoDB collection
        users_collection.insert_one({'firstName': 'John', 'lastName': 'Doe', 'email': 'johndoe@example.com', 'password': 'password123'})

        response = self.app.post('/register', data={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'confirmPass': 'password123'
        })
        self.assertEqual(response.status_code, 200)  # Expect 200 OK, meaning it stays on the same page
        self.assertIn(b"email already registered", response.data)  # Check if the error message is in the response

    @classmethod
    def tearDownClass(cls):
        # Clean up the users collection after all tests
        users_collection.delete_many({})

if __name__ == '__main__':
    unittest.main() # pragma: no cover 
