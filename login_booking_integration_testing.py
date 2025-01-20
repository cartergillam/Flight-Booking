import unittest
from app import app, users_collection, bookings_collection

class BookingHistoryTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and test database."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear previous entries in MongoDB collections
        users_collection.delete_many({})
        bookings_collection.delete_many({})
        
        # Insert a test user in the MongoDB collection
        self.test_user_email = 'testuser@gmail.com'
        self.test_user_password = 'password123'
        self.test_user_data = {
            'firstName': 'Test',
            'lastName': 'User',
            'email': self.test_user_email,
            'password': self.test_user_password
        }
        users_collection.insert_one(self.test_user_data)

        # Insert test bookings for the user
        self.test_bookings = [
            {
                'user_email': self.test_user_email,
                'departureSeat': '12A',
                'returnSeat': '14B',
                'trip_type': 'round_trip',
                'to_city': 'CityA',
                'from_city': 'CityB'
            },
            {
                'user_email': self.test_user_email,
                'departureSeat': '15C',
                'trip_type': 'one_way',
                'to_city': 'CityC',
                'from_city': 'CityD'
            }
        ]
        bookings_collection.insert_many(self.test_bookings)

    def test_booking_history(self):
        # Log in the test user
        response = self.app.post('/login', data={
            'email': self.test_user_email,
            'password': self.test_user_password
        }, follow_redirects=True)
        
        # Check if login was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'flightSearch', response.data)

        # Access the booking history page
        response = self.app.get('/booking-history', follow_redirects=True)

        # Check response status
        self.assertEqual(response.status_code, 200)  # Expect 200 OK

        # Verify the booking history content
        self.assertIn(b'12A', response.data)
        self.assertIn(b'14B', response.data)
        self.assertIn(b'15C', response.data)
        self.assertIn(b'CityA', response.data)
        self.assertIn(b'CityC', response.data)

if __name__ == '__main__':
    unittest.main()