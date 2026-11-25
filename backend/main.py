from pathlib import Path
import joblib
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from feature_extractor import extract_features, features_to_vector
from qr_decoder import decode_qr

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
MODEL_PATH = BASE_DIR / "model" / "gb_phishing_model.pkl"

_model_bundle = None

app = FastAPI(title="QR Phishing Detector", version="1.0.0")

if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )


def load_model():
    """Load the trained model once and reuse it for later requests."""
    global _model_bundle

    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(
                f"Model file not found: {MODEL_PATH}. "
                "A trained gb_phishing_model.pkl is required."
            )
        _model_bundle = joblib.load(MODEL_PATH)

    return _model_bundle


@app.get("/")
async def home():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "QR Phishing Detector API is running."}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model_file_exists": MODEL_PATH.exists(),
    }


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        url = decode_qr(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not url.lower().startswith(("http://", "https://")):
        raise HTTPException(
            status_code=422,
            detail=f"QR content is not an HTTP/HTTPS URL: {url!r}",
        )

    features = extract_features(url)
    feature_vector = np.asarray(
        features_to_vector(features), dtype=float
    ).reshape(1, -1)

    try:
        bundle = load_model()
    except (RuntimeError, OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    model = bundle["model"]

    try:
        probabilities = model.predict_proba(feature_vector)[0].tolist()
        prediction = int(model.predict(feature_vector)[0])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {exc}",
        ) from exc

    # The report's model uses 0 = SAFE and 1 = PHISHING.
    is_phishing = bool(prediction)
    confidence = probabilities[1] if is_phishing else probabilities[0]

    return {
        "url": url,
        "is_phishing": is_phishing,
        "label": "PHISHING" if is_phishing else "SAFE",
        "confidence": round(float(confidence), 4),
        "phishing_probability": round(float(probabilities[1]), 4),
        "safe_probability": round(float(probabilities[0]), 4),
        "features": features,
        "model_info": {
            "accuracy": bundle.get("accuracy"),
            "auc": bundle.get("auc"),
        },
    }
