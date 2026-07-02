/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API bazaviy URL (prod build uchun). Dev'da bo'sh -> `/api/v1` proxy. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
