from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.datasets import load_digits
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np

app = Flask(__name__)
CORS(app)


def train_model():
    digits = load_digits()
    x = digits.data
    y = digits.target
    model = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            max_iter=400,
            random_state=42,
        ),
    )
    model.fit(x, y)
    return model


MODEL = train_model()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True)
    if not payload or "pixels" not in payload:
        return jsonify({"error": "Missing 'pixels' array in request body."}), 400

    pixels = np.array(payload["pixels"], dtype=float)
    if pixels.size != 64:
        return jsonify({"error": "Expected 64 pixel values (8x8)."}), 400

    pixels = pixels.reshape(1, -1)
    probabilities = MODEL.predict_proba(pixels)[0]
    prediction = int(np.argmax(probabilities))

    return jsonify(
        {
            "prediction": prediction,
            "probabilities": {
                str(idx): float(prob) for idx, prob in enumerate(probabilities)
            },
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
