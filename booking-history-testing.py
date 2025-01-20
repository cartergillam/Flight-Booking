import unittest
from app import app, bookings_collection, users_collection

class BookingHistoryTestCase(unittest.TestCase):

    # Set up the Flask test client
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Clear collections before each test
        bookings_collection.delete_many({})
        users_collection.delete_many({})

        # Add a test user and log them in
        self.user_email = "terencejiang@gmail.com"
        self.user_data = {
            "firstName": "Terence",
            "lastName": "Jiang",
            "email": self.user_email,
            "password": "password123"
        }
        users_collection.insert_one(self.user_data)
        with self.app:
            self.app.post('/login', data={
                'email': self.user_email,
                'password': self.user_data['password']
            })

    # Test accessing booking history while logged in
    def test_booking_history_authenticated(self):
        # Add a mock booking for the test user
        bookings_collection.insert_one({
            "user_email": self.user_email,
            "departureSeat": "12A",
            "returnSeat": "15B",
            "trip_type": "round_trip",
            "to_city": "Toronto",
            "from_city": "Vancouver"
        })

        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_email'] = self.user_email

            # Access the booking history
            response = client.get('/booking-history')

            # Check if the response contains booking details
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Toronto", response.data)
            self.assertIn(b"Vancouver", response.data)
            self.assertIn(b"12A", response.data)

    # Test accessing booking history without logging in
    def test_booking_history_unauthenticated(self):
        with self.app:
            self.app.get('/logout')  # Log out the user if logged in

            response = self.app.get('/booking-history')

            # Should redirect to login page if not authenticated
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login', response.location)

    # Clean up after each test
    def tearDown(self):
        bookings_collection.delete_many({})
        users_collection.delete_many({})

if __name__ == '__main__':
    unittest.main() # pragma: no cover
