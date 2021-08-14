import unittest
from utility import *


# Test utility.py
class UtilityTests(unittest.TestCase):

    def test_significant_digit_check(self):
        self.assertTrue(check_significant_digits(1.2300000001, 3))
        self.assertTrue(check_significant_digits(136.00000001, 3))
        self.assertFalse(check_significant_digits(135.1110, 4))
        self.assertFalse(check_significant_digits(1.111, 2))

    def test_period_to_frequency_conversion(self):
        self.assertAlmostEqual(period_to_frequency_mhz_precision(33.333), 30, delta=0.1)
        self.assertAlmostEqual(period_to_frequency_mhz_precision(0.938), 1066, delta=0.1)

    def test_frequency_to_period_conversion(self):
        self.assertAlmostEqual(frequency_to_period_ns_precision(30), 33.333, delta=0.001)
        self.assertAlmostEqual(frequency_to_period_ns_precision(19), 52.631, delta=0.001)
