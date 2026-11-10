import { useState } from 'react';
import './App.css'

function App() {
  const [url, setUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    alert(`submitted ${url}`);
  }
  
  return (
    <>
      <h1>Checking your URL links</h1>
      <p>Enter a link and our machine-learning model will
        check it dor signs of phishing.
      </p>
      <div>
          <form onSubmit={handleSubmit}>
            <input 
          type="url" 
          placeholder='https://example' 
          onChange={(event) => setUrl(event.target.value)}
          maxLength={8000}
          required
          />

          <button type="submit">
            Sumbit URL
          </button>
          </form>
          
        </div>
    </>
  )
}

export default App
