import unittest
from flask import session
from app import app, users_collection 


class TestUserRegistrationAndLogin(unittest.TestCase):
    def setUp(self):
        """Set up test client and test database."""
        self.app = app.test_client()
        self.app.testing = True

        # Use a test database
        self.db = users_collection
        self.test_user = {
            "firstName": "Test",
            "lastName": "User",
            "email": "testuser@example.com",
            "password": "password123"
        }

        # Ensure a clean slate before testing
        self.db.delete_many({"email": self.test_user['email']})

    def tearDown(self):
        """Clean up after tests."""
        self.db.delete_many({"email": self.test_user['email']})

    def test_user_registration_and_login(self):
        """Test the user registration and login process."""

        # Step 1: Register a new user
        response = self.app.post('/register', data={
            "firstName": self.test_user['firstName'],
            "lastName": self.test_user['lastName'],
            "email": self.test_user['email'],
            "password": self.test_user['password'],
            "confirmPass": self.test_user['password']
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect after registration
        self.assertIn('/login', response.location)   # Ensure it redirects to the login page

        # Verify the user is in the database
        user_in_db = self.db.find_one({"email": self.test_user['email']})
        self.assertIsNotNone(user_in_db)
        self.assertEqual(user_in_db['email'], self.test_user['email'])

        # Step 2: Log in with the registered user
        response = self.app.post('/login', data={
            "email": self.test_user['email'],
            "password": self.test_user['password']
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Ensure successful page load

        # Verify session contains the logged-in user's email
        with self.app.session_transaction() as session_data:
            self.assertEqual(session_data['user_email'], self.test_user['email'])

        # Verify the response contains content indicating successful login
        self.assertIn(b'Welcome', response.data)  


if __name__ == '__main__':
    unittest.main()
