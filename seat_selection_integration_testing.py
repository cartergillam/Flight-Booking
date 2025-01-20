import unittest
from flask import session
from app import app, users_collection, bookings_collection

class SeatSelectionTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and test database."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear previous entries in MongoDB collections
        users_collection.delete_many({})
        bookings_collection.delete_many({})
        
        # Insert an existing user in the MongoDB collection for testing
        self.existing_user = 'johndoe@gmail.com'
        self.existing_user_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': self.existing_user,
            'password': 'password123'
        }
        users_collection.insert_one(self.existing_user_data)

    def test_seat_selection_logged_in(self):
        """Test seat selection for logged-in user."""
        with self.app.session_transaction() as sess:
            sess['user_email'] = self.existing_user
        
        response = self.app.get('/seat-selection', follow_redirects=True)
        
        # Check for successful page load (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Simulate seat selection
        response = self.app.post('/save-seat-selection', json={
            'departureSeat': '12A',
            'returnSeat': '14B'
        }, follow_redirects=True)
        
        # Check response for success
        self.assertEqual(response.status_code, 200)
        
        # Verify seat selection was saved in the database
        booking = bookings_collection.find_one({"user_email": self.existing_user})
        self.assertIsNotNone(booking)
        self.assertEqual(booking['departureSeat'], '12A')
        self.assertEqual(booking['returnSeat'], '14B')

    def test_seat_selection_not_logged_in(self):
        """Test seat selection when user is not logged in."""
        response = self.app.get('/seat-selection', follow_redirects=True)
        
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)  # Check if 'Login' appears on the page

if __name__ == '__main__':
    unittest.main()
