import unittest
from utility import *


# Test utility.py
class UtilityTests(unittest.TestCase):

    def test_period_to_frequency_conversion(self):
        self.assertAlmostEqual(period_to_frequency_mhz_precision(33.333), 30, delta=0.1)
        self.assertAlmostEqual(period_to_frequency_mhz_precision(0.938), 1066, delta=0.1)

    def test_frequency_to_period_conversion(self):
        self.assertAlmostEqual(frequency_to_period_ns_precision(30), 33.333, delta=0.001)
        self.assertAlmostEqual(frequency_to_period_ns_precision(19), 52.631, delta=0.001)

    def test_relative_error(self):
        self.assertEqual(relative_error(100, 37), 0.63)
        self.assertEqual(relative_error(100, -37), 1.37)
        self.assertEqual(relative_error(50, 22), 28/50)
        self.assertEqual(relative_error(-50, 22), 72/50)
