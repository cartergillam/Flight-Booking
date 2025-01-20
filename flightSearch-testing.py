import unittest
from app import app, users_collection, bookings_collection

class FlightSearchTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Clear previous entries in MongoDB collections
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

        # Set up a session for the user
        with self.app.session_transaction() as sess:
            sess['user_email'] = self.existing_user

    def test_flight_search_get(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Input Form', response.data)  # Check if the form is loaded

    def test_flight_search_post(self):
        response = self.app.post('/', data={
            'flightType': 'one_way',
            'from': 'New York',
            'to': 'Los Angeles'
        })


        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mock Flight Available', response.data)  # Check if mock flight details are shown
        self.assertIn(b'Flight Type:', response.data)  # Check if flight type is displayed

    def test_flight_search_post_round_trip(self):
        response = self.app.post('/', data={
            'flightType': 'round_trip',
            'from': 'Chicago',
            'to': 'Miami'
        })


        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mock Flight Available', response.data)  # Check if mock flight details are shown
        self.assertIn(b'Flight Type:', response.data)  # Check if flight type is displayed

    def tearDown(self):
        # Clean up MongoDB after each test
        users_collection.delete_many({})
        bookings_collection.delete_many({})

if __name__ == '__main__':
    unittest.main() # pragma: no cover 
