import unittest
from app import app, users_collection  # Import your app and database

class ProfileManagementTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear previous entries in MongoDB collection
        users_collection.delete_many({})  
        
        # Insert an existing user in the MongoDB collection for testing
        self.existing_user = 'johndoe@gmail.com'
        self.existing_user_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': self.existing_user,
            'password': 'password123'
        }
        users_collection.insert_one(self.existing_user_data)

    # Test case for successful profile update
    def test_successful_profile_update(self):
        response = self.app.post(f'/profile/{self.existing_user}', data={
            'firstName': 'Johnny',
            'lastName': 'Doe',
            'email': 'johnnydoe@gmail.com',
            'password': 'newpassword123',
            'confirmPass': 'newpassword123',
            'action': 'Save Changes'
        }, follow_redirects=True)

        # Check response status
        self.assertEqual(response.status_code, 200)  # Expect 200 OK after redirection

        # Query MongoDB for updated user information
        updated_user = users_collection.find_one({"email": "johnnydoe@gmail.com"})
        self.assertIsNotNone(updated_user)  # Check if new email exists
        self.assertEqual(updated_user['firstName'], 'Johnny')
        self.assertEqual(updated_user['email'], 'johnnydoe@gmail.com')
        self.assertEqual(updated_user['password'], 'newpassword123')

        # Ensure the old email no longer exists in MongoDB
        old_user = users_collection.find_one({"email": self.existing_user})
        self.assertIsNone(old_user)

    # Test case for when passwords do not match
    def test_password_mismatch(self):
        response = self.app.post(f'/profile/{self.existing_user}', data={
            'firstName': 'Johnny',
            'lastName': 'Doe',
            'email': 'johnnydoe@gmail.com',
            'password': 'newpassword123',
            'confirmPass': 'wrongpassword123',
            'action': 'Save Changes'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)  # Expect 200 OK
        self.assertIn(b"Passwords do not match", response.data)
        
        # Ensure MongoDB data hasn't been altered
        user = users_collection.find_one({"email": self.existing_user})
        self.assertEqual(user['firstName'], 'John')

    # Test case for missing fields (empty email)
    def test_missing_field(self):
        response = self.app.post(f'/profile/{self.existing_user}', data={
            'firstName': 'Johnny',
            'lastName': 'Doe',
            'email': '',
            'password': 'newpassword123',
            'confirmPass': 'newpassword123',
            'action': 'Save Changes'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Expect 200 OK
        self.assertIn(b"All fields must be filled.", response.data)
        
        # Ensure MongoDB data hasn't been altered
        user = users_collection.find_one({"email": self.existing_user})
        self.assertEqual(user['firstName'], 'John')

    # Test case for discarding changes
    def test_discard_changes(self):
        response = self.app.post(f'/profile/{self.existing_user}', data={
            'firstName': 'Johnny',
            'lastName': 'Doe',
            'email': 'johnnydoe@gmail.com',
            'password': 'newpassword123',
            'confirmPass': 'newpassword123',
            'action': 'Discard Changes'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)  # Expect 200 OK after redirection
        
        # Ensure no changes have been made in MongoDB
        user = users_collection.find_one({"email": self.existing_user})
        self.assertEqual(user['firstName'], 'John')
        self.assertEqual(user['email'], 'johndoe@gmail.com')
        
        # Ensure the new email does not exist in MongoDB
        self.assertIsNone(users_collection.find_one({"email": "johnnydoe@gmail.com"}))

    def tearDown(self):
        # Clean up MongoDB after each test
        users_collection.delete_many({})


if __name__ == '__main__':
    unittest.main() # pragma: no cover 
