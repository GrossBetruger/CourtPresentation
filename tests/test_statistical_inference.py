import unittest
from random import random

from confidence_intervals import calc_confidence_interval, manual_ci_sample


class TestConfidenceInterval(unittest.TestCase):
    def test_api_and_manual_calculation(self):
        sample = [random() * 100 for _ in range(30)]
        for conf in [0.95, 0.99, 0.999]:
            ci_scipy = calc_confidence_interval(sample, conf)
            _, scipy_lower, scipy_upper, _ = ci_scipy
            ci_manual = manual_ci_sample(sample, conf)
            manual_lower, manual_upper = ci_manual
            self.assertAlmostEqual(scipy_lower, manual_lower, delta=0.000000001)
            self.assertAlmostEqual(scipy_upper, manual_upper, delta=0.000000001)


if __name__ == '__main__':
    unittest.main()
