from contextlib import asynccontextmanager
import ipaddress
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlsplit

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator


MODEL_PATH = Path(__file__).resolve().parent / "URL_Phishing_model.joblib"
FEATURE_NAMES = (
    "url_length",
    "domain_length",
    "is_https",
    "is_ip",
    "letter_count",
    "digit_count",
    "special_count",
    "eq_count",
    "qm_count",
    "amp_count",
    "dot_count",
    "dash_count",
    "under_count",
    "letter_ratio",
    "special_ratio",
    "digit_ratio",
)
PHISHING_LABEL = 0
LEGITIMATE_LABEL = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    app.state.model = joblib.load(MODEL_PATH)
    yield
    del app.state.model


app = FastAPI(lifespan=lifespan)


class PredictionRequest(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=5000)]

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        try:
            parsed = urlsplit(value)
            valid_url = (
                parsed.scheme.lower() in {"http", "https"} and parsed.hostname is not None
            )
            parsed.port
        except ValueError as error:
            raise ValueError("Enter a valid URL starting with http:// or https://.") from error

        if not value or not valid_url:
            raise ValueError("Enter a full URL starting with http:// or https://.")
        return value


class PredictionResponse(BaseModel):
    url: str
    label: str
    is_phishing: bool
    confidence: float | None = None


def extract_features(url: str) -> dict[str, int | float]:
    parsed = urlsplit(url)
    hostname = parsed.hostname or ""
    url_length = len(url)
    letter_count = sum(character.isalpha() for character in url)
    digit_count = sum(character.isdigit() for character in url)
    special_count = sum(not character.isalnum() for character in url)

    try:
        ipaddress.ip_address(hostname)
        is_ip = 1
    except ValueError:
        is_ip = 0

    return {
        "url_length": url_length,
        "domain_length": len(hostname),
        "is_https": int(parsed.scheme.lower() == "https"),
        "is_ip": is_ip,
        "letter_count": letter_count,
        "digit_count": digit_count,
        "special_count": special_count,
        "eq_count": url.count("="),
        "qm_count": url.count("?"),
        "amp_count": url.count("&"),
        "dot_count": url.count("."),
        "dash_count": url.count("-"),
        "under_count": url.count("_"),
        "letter_ratio": letter_count / url_length,
        "special_ratio": special_count / url_length,
        "digit_ratio": digit_count / url_length,
    }


def is_phishing_label(label: Any) -> bool:
    if isinstance(label, str):
        normalized = label.strip().lower()
        if normalized in {"phishing", "phish", "malicious", "bad", "1", "true"}:
            return True
        if normalized in {"legitimate", "legit", "benign", "safe", "good", "0", "false"}:
            return False
    elif label == PHISHING_LABEL:
        return True
    elif label == LEGITIMATE_LABEL:
        return False

    raise ValueError(f"Unrecognized model prediction label: {label!r}")


def predict_url(payload: PredictionRequest, model: Any) -> PredictionResponse:
    features = extract_features(payload.url)
    model_features = getattr(model, "feature_names_in_", FEATURE_NAMES)
    missing_features = set(model_features) - features.keys()
    if missing_features:
        raise RuntimeError(
            "The model expects URL features that are not available: "
            + ", ".join(sorted(missing_features))
        )

    feature_frame = pd.DataFrame(
        [[features[name] for name in model_features]],
        columns=model_features,
    )
    raw_prediction = model.predict(feature_frame)[0]
    try:
        phishing = is_phishing_label(raw_prediction)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    confidence = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(feature_frame)[0]
        classes = getattr(model, "classes_", ())
        if len(classes) == len(probabilities):
            prediction_index = list(classes).index(raw_prediction)
            confidence = float(probabilities[prediction_index])

    return PredictionResponse(
        url=payload.url,
        label="Phishing" if phishing else "Likely legitimate",
        is_phishing=phishing,
        confidence=confidence,
    )


@app.post("/api/predict", response_model=PredictionResponse)
def check(payload: PredictionRequest, request: Request) -> PredictionResponse:
    return predict_url(payload, request.app.state.model)
