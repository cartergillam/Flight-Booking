import unittest
from app import app, users_collection  # Import the app and mock database

class LogInTestCase(unittest.TestCase):

    # Set up the Flask test client
    def setUp(self):
        self.app = app.test_client()  # Flask's test client
        self.app.testing = True
        users_collection.delete_many({})  # Clear users collection before each test
    
    # Test login with valid credentials
    def test_login_success(self):
        # First, register a user
        users_collection.insert_one({
            'firstName': 'Terence',
            'lastName': 'Jiang',
            'email': 'terencejiang@gmail.com',
            'password': 'password123'
        })

        response = self.app.post('/login', data={
            'email': 'terencejiang@gmail.com',
            'password': 'password123'
        })
        
        # Expect a redirect to the profile page upon successful login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.location)  # Check redirection URL

    # Test login with incorrect password
    def test_login_incorrect_password(self):
        # Insert a test user into MongoDB
        users_collection.insert_one({
            'firstName': 'Jack',
            'lastName': 'Cam',
            'email': 'jackcam@gmail.com',
            'password': 'password123'
        })

        response = self.app.post('/login', data={
            'email': 'jackcam@gmail.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertIn(b'Email and password does not match', response.data)  # Check if the error message is shown

    # Test login with unregistered email
    def test_login_unregistered_email(self):
        response = self.app.post('/login', data={
            'email': 'nonexistent@gmail.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertIn(b'The provided email is not registered', response.data)  # Check if the error message is shown

    # Test login with mismatched credentials
    def test_invalid_login(self):
        response = self.app.post('/login', data={
            'email': 'wrong@email.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)

    # Test login with missing fields
    def test_missing_fields(self):
        response = self.app.post('/login', data={
            'email': 'test@test.com'
        })
        self.assertEqual(response.status_code, 400)

     # Tear down any modifications to the database after each test
    def tearDown(self):
        users_collection.delete_many({})  # Clear users collection after each test

if __name__ == '__main__':
    unittest.main() # pragma: no cover
