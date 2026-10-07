# AgriScan — Frontend Bundle

This is the **website** side of AgriScan only — a React app. It has no backend
code in it at all; it just makes HTTP requests to the backend (see the separate
`agriscan-backend` package).

## Folder guide

```
src/
  pages/        ← one file per page: Landing, Scan, Result, StoreLocator, About
  components/   ← small reusable pieces (Navbar, TreatmentCard)
  api/          ← client.ts (the actual fetch calls to the backend) and
                  DiagnosisContext.tsx (passes the scan result between pages)
  styles/       ← global CSS
index.html      ← entry HTML, loads the fonts
package.json    ← dependencies
vite.config.ts, tsconfig.json, tailwind.config.js, postcss.config.js  ← build tooling
Dockerfile      ← builds this into a static site served by nginx
```

## To run it

```bash
npm install
cp .env.example .env   # points it at http://localhost:8000 — start the backend first
npm run dev
```

Then open the printed localhost URL. The Scan page really uploads to the
backend and shows whatever it returns — nothing here is faked on the frontend
side (any "mock" behavior lives in the backend, not here).
