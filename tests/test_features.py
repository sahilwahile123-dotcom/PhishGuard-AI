import unittest
from src.feature_extraction import FEATURE_NAMES, extract_features

class FeatureTests(unittest.TestCase):
    def test_normal(self):
        f = extract_features("https://www.example.com/path")
        self.assertEqual(list(f), FEATURE_NAMES)
        self.assertEqual((f["is_https"], f["has_ip"], f["num_subdomains"]), (1, 0, 1))
    def test_ip_port_at(self):
        f = extract_features("http://192.168.1.1:8080/login@x")
        self.assertEqual((f["has_ip"], f["unusual_port"], f["has_at"], f["keyword_count"]), (1, 1, 1, 1))
    def test_shortener(self):
        self.assertEqual(extract_features("https://bit.ly/abc")["is_shortener"], 1)
    def test_suspicious_string(self):
        f = extract_features("http://secure-login.verify-account.example.tk/update?id=1&x=%20")
        self.assertGreaterEqual(f["keyword_count"], 3); self.assertGreaterEqual(f["num_hyphens"], 2)
    def test_invalid(self):
        for bad in ["", "   ", "ftp://x.com", "http://", "a b.com", "x" * 3000, None, 5, "http://a..com"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                extract_features(bad)

if __name__ == "__main__":
    unittest.main()
