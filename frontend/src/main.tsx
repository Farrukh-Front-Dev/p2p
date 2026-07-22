import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@/shared/lib/i18n';
import App from './app/App';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
