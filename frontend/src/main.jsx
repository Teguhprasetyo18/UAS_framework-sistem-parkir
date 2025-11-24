import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

function checkMasuk() {
  fetch("http://localhost:8000/parkir/checkin/")
    .then(res => res.json())
    .then(data => {
      alert("Kendaraan masuk: " + data.nomor_plat);
});
}
