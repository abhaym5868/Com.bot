# Changelog Widget — Frontend

## Stack
- React 18 + Vite 5
- Axios (API client with interceptors)
- React Router DOM v6
- react-markdown + remark-gfm (Markdown rendering)

## Development

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`.

## Environment Variables

Create a `.env` file (optional, Vite proxy handles dev):

```env
VITE_API_URL=http://localhost:8000
```

## Proxy
Vite proxies `/api` requests to `http://127.0.0.1:8000` during development,
so no CORS issues in dev.
