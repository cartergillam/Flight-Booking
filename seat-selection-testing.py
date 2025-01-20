import unittest
from app import app, users_collection, bookings_collection

class SeatSelectionTestCase(unittest.TestCase):

    def setUp(self):
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

        # Set up a session for the user
        with self.app.session_transaction() as sess:
            sess['user_email'] = self.existing_user

    def test_seat_selection_page_load(self):
        response = self.app.get('/seat-selection')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Flight Seat Selection', response.data)

    def test_get_trip_info(self):
        response = self.app.get('/get-trip-info')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('isRoundTrip', data)
        self.assertIn('passengerName', data)
        self.assertIn('tripType', data)

    def test_save_seat_selection_one_way(self):
        response = self.app.post('/save-seat-selection', json={
            'departureSeat': '1A',
            'returnSeat': None
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Check if booking was saved in MongoDB
        booking = bookings_collection.find_one({"user_email": self.existing_user})
        self.assertIsNotNone(booking)
        self.assertEqual(booking['departureSeat'], '1A')
        self.assertIsNone(booking['returnSeat'])

    def test_save_seat_selection_round_trip(self):
        # Set trip type to round trip
        with self.app.session_transaction() as sess:
            sess['trip_type'] = 'round_trip'

        response = self.app.post('/save-seat-selection', json={
            'departureSeat': '2B',
            'returnSeat': '3C'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Check if booking was saved in MongoDB
        booking = bookings_collection.find_one({"user_email": self.existing_user})
        self.assertIsNotNone(booking)
        self.assertEqual(booking['departureSeat'], '2B')
        self.assertEqual(booking['returnSeat'], '3C')

    def test_clear_bookings(self):
        # First, create a booking
        bookings_collection.insert_one({
            "user_email": self.existing_user,
            "departureSeat": "4D",
            "returnSeat": "5E",
            "trip_type": "round_trip"
        })
        response = self.app.get('/clear-bookings', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check if bookings were cleared
        bookings = list(bookings_collection.find({"user_email": self.existing_user}))
        self.assertEqual(len(bookings), 0)

    def tearDown(self):
        # Clean up MongoDB after each test
        users_collection.delete_many({})
        bookings_collection.delete_many({})

if __name__ == '__main__':
    unittest.main() # pragma: no cover 