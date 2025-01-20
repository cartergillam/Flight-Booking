import coverage
import unittest

# Initialize a Coverage object
cov = coverage.Coverage()

# Start coverage measurement
cov.start()

# Discover and run tests
loader = unittest.TestLoader()
suite = loader.discover('login-testing') 

runner = unittest.TextTestRunner()
runner.run(suite)

# Stop coverage measurement
cov.stop()
cov.save()

# Display coverage report in the terminal
cov.report(show_missing=True)
