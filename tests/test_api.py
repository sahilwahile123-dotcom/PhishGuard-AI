import tempfile, unittest
from pathlib import Path
import pandas as pd
from app import create_app
from src.predict import Predictor
from src.train_model import train

def pipeline_fixture():
    """TEST FIXTURE ONLY - made-up URLs to exercise the code. Never used for the real model."""
    good = [f"https://www.site{i}.com/page/{i}" for i in range(60)]
    bad = [f"http://192.168.{i}.1:8080/secure-login-verify-account@x?id={i}" for i in range(60)]
    return pd.DataFrame({"url": good + bad, "y": [0] * 60 + [1] * 60})

class ApiTests(unittest.TestCase):
    def test_untrained(self):
        d = Path(tempfile.mkdtemp())
        c = create_app(Predictor(d / "m.joblib", d / "x.json")).test_client()
        self.assertEqual(c.get("/api/health").json["model_ready"], False)
        self.assertEqual(c.post("/api/scan", json={"url": "https://a.com"}).status_code, 503)
        self.assertEqual(c.post("/api/scan", json={"url": ""}).status_code, 400)
        self.assertEqual(c.post("/api/scan", json={"url": 5}).status_code, 400)
        self.assertEqual(c.post("/api/scan", data="nope").status_code, 400)
        self.assertEqual(c.get("/").status_code, 200)
    def test_trained_pipeline(self):
        d = Path(tempfile.mkdtemp())
        m = train(pipeline_fixture(), d / "m.joblib", d / "x.json", "test-fixture")
        self.assertIn("accuracy", m)
        c = create_app(Predictor(d / "m.joblib", d / "x.json")).test_client()
        r = c.post("/api/scan", json={"url": "http://10.0.0.5:8080/secure-login-verify-account@x?id=3"})
        self.assertEqual(r.status_code, 200); self.assertEqual(r.json["classification"], "Phishing")
        self.assertEqual(c.post("/api/scan", json={"url": "https://www.site3.com/page/3"}).json["classification"], "Legitimate")
        self.assertTrue(c.get("/api/model-info").json["metrics"]["test_size"] > 0)

if __name__ == "__main__":
    unittest.main()
