import hashlib
import tempfile
from pathlib import Path


MODEL_ID = "1NWXzV82bp_GWocWsQQgbpcwODAyR5bbc"
MODEL_SHA256 = "c379b9cab9db10897fcc21722fdde11fe324265b9c1e90e19335f259ecd36e0e"
MODEL_PATH = Path(__file__).resolve().parent / "URL_Phishing_model.joblib"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_model() -> None:
    if MODEL_PATH.is_file() and sha256_file(MODEL_PATH) == MODEL_SHA256:
        print(f"Model is already downloaded: {MODEL_PATH}")
        return

    try:
        import gdown
    except ImportError as error:
        raise SystemExit(
            "gdown is required. Install project dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from error

    with tempfile.TemporaryDirectory(dir=MODEL_PATH.parent) as temporary_directory:
        temporary_path = Path(temporary_directory) / MODEL_PATH.name
        result = gdown.download(
            id=MODEL_ID,
            output=str(temporary_path),
            quiet=False,
        )
        if result is None or not temporary_path.is_file():
            raise RuntimeError("Google Drive did not return the model file.")

        actual_sha256 = sha256_file(temporary_path)
        if actual_sha256 != MODEL_SHA256:
            raise RuntimeError(
                "Downloaded model checksum does not match the expected model. "
                "The existing model file was not replaced."
            )

        temporary_path.replace(MODEL_PATH)

    print(f"Downloaded and verified model: {MODEL_PATH}")


if __name__ == "__main__":
    download_model()
