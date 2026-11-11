# URL Phishing Checker

## Run locally

Install the Python dependencies and download the model from Google Drive:

```powershell
python -m pip install -r requirements.txt
python download_model.py
```

The download script saves `URL_Phishing_model.joblib` in the project directory
and checks its SHA-256 checksum before accepting it. The model file is ignored
by Git because it is a large generated download.

Start the API from the project directory:

```powershell
python -m uvicorn main:app --reload
```

In another terminal, start the React app:

```powershell
npm install
npm run dev
```

The API loads `URL_Phishing_model.joblib` from the project directory. During
development, Vite forwards `/api` requests to `http://127.0.0.1:8000`.

The API currently interprets the model's numeric class `1` as phishing and
class `0` as legitimate. Make sure that matches how the model's training labels
were encoded.
