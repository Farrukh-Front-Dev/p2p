# P2P Corpus — School21 Peer-to-Peer Learning Platform

This is the complete, modern cyber-minimalist frontend application for **P2P Corpus**, a peer-to-peer learning and assessment platform built for School21 students.

---

## 🛠️ Tech Stack & Standards

- **Framework:** React 19 + Vite + TypeScript (strict mode)
- **Styling:** Tailwind CSS v4 running optimized `@theme` tokens in `src/index.css`
- **Queries:** `@tanstack/react-query` v5 for asynchronous server state
- **Stores:** `zustand` with persisted client store profiles (auth, telemetry keys)
- **Icons:** `lucide-react`
- **Forms:** `react-hook-form` + `zod` schema verification

---

## 🚀 Setup & Run Instructions

Follow these simple steps to run the frontend application locally:

### 1. Install Dependencies
Make sure you have Node.js (version 18 or above recommended) installed, and run:
```bash
npm install
```

### 2. Configure Environment Variables
Copy `.env.example` into a local configuration and set up any custom parameters:
```bash
cp .env.example .env
```

### 3. Launch Development Server
Launch the Vite development workspace:
```bash
npm run dev
```
The application will launch on port **3000** automatically (or port **5173** during vanilla local development).

---

## 📡 Backend API & Proxy Configuration

To prevent Cross-Origin Resource Sharing (CORS) blocks, Vite is configured with a built-in reverse proxy forwarding:
- REST queries from `/api` to the FastAPI backend origin (`http://localhost:8000`).
- Real-time updates from `/ws` via secure WebSockets.

Refer to `vite.config.ts` for exact settings:
```ts
server: {
  port: 3000,
  host: "0.0.0.0",
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true },
    '/ws':  { target: 'ws://localhost:8000', ws: true },
  },
}
```

---

## 🎯 Guest Bypass Mode (Demo / Admin Bypasses)

For rapid evaluations or if the backend servers are unavailable, the application contains a fully featured offline sandbox mode.
- Log in using `demo` or `admin` as the School21 username on the login screen.
- This triggers our Custom Axios Adapter (offline sandbox) built within `src/lib/axios.ts` to seamlessly populate mock data representing dashboards, active slot countdowns, user achievements, leaderboard logs, and notifications.
