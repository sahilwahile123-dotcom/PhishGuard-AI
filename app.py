from flask import Flask, jsonify, render_template, request
from config import MAX_URL_LENGTH
from src.feature_extraction import FEATURE_NAMES
from src.predict import ModelNotTrained, Predictor

def create_app(predictor=None):
    app = Flask(__name__)
    pred = predictor or Predictor()

    @app.get("/")
    def index():
        return render_template("index.html", max_len=MAX_URL_LENGTH)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", model_ready=pred.ready)

    @app.get("/api/model-info")
    def model_info():
        pred.reload()
        return jsonify(model_ready=pred.ready, features=FEATURE_NAMES, metrics=pred.metrics,
                       message=None if pred.ready else "No trained model. Follow README step 'Train the model'.")

    @app.post("/api/scan")
    def scan():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("url"), str):
            return jsonify(error="Send JSON like {\"url\": \"https://example.com\"}."), 400
        try:
            return jsonify(pred.scan(data["url"]))
        except ValueError as e:
            return jsonify(error=str(e)), 400
        except ModelNotTrained:
            return jsonify(error="Model not trained yet. Add a dataset and run: python -m src.train_model", setup_required=True), 503
        except Exception:
            app.logger.exception("scan failed")
            return jsonify(error="Internal error while analysing the URL."), 500

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
