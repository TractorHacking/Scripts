import unittest

# Aped from SO:
# https://stackoverflow.com/a/37033551
def my_test_suite():
  test_loader = unittest.TestLoader()
  test_suite = test_loader.discover('tests', pattern='test_*.py')
  return test_suite
