import { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const submittedUrl = url.trim();
    setResult(null);
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: submittedUrl }),
      });
      const data = await response.json();

      if (!response.ok) {
        const detail = data.detail;
        const message = Array.isArray(detail)
          ? detail.map((item) => item.msg).join(" ")
          : detail;
        throw new Error(message || "The URL could not be checked.");
      }

      setResult(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the prediction service.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <h1>Checking your URL links</h1>
      <p>
        Enter a link and our machine-learning model will check it for signs of
        phishing.
      </p>
      <div>
        <form onSubmit={handleSubmit}>
          <input
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            maxLength={5000}
            required
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Checking..." : "Submit URL"}
          </button>
        </form>
        {error && (
          <p className="prediction-error" role="alert">
            {error}
          </p>
        )}
        {result && (
          <section
            className={
              result.is_phishing
                ? "prediction-result result-phishing"
                : "prediction-result result-legitimate"
            }
            aria-live="polite"
            aria-label="URL prediction"
          >
            <span className="result-icon" aria-hidden="true">
              {result.is_phishing ? "!" : "✓"}
            </span>
            <div className="result-details">
              <p className="result-eyebrow">MODEL ASSESSMENT</p>
              <h2>{result.label}</h2>
              <p className="result-url">{result.url}</p>
            </div>
            {typeof result.confidence === "number" && (
              <span className="result-confidence">
                {Math.round(result.confidence * 100)}%
                <span>confidence</span>
              </span>
            )}
          </section>
        )}
      </div>
    </>
  );
}

export default App;
