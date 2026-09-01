# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project overview
- Frontend web app built with Vite/React, React 18, and React Router.
- Authentication uses SIT Brightspace LTI 1.3 for students and ADFS/MSAL for staff entry.
- UAT is deployed as a local Docker stack: frontend/nginx, lti-backend, backend-api, PostgreSQL, and Redis.
- Deployed frontend assets are served by Nginx; docker-entrypoint.sh writes runtime env config and same-origin proxy config.

Common commands
- Install dependencies
  - npm install
- Start dev server (http://localhost:3000)
  - npm start
- Build for production
  - npm run build
- Run tests (Jest via react-scripts)
  - All tests (interactive watch): npm test
  - Single test file: npm test -- src/App.test.js
  - Filter by test name: npm test -- -t "some test name"
  - Run once in CI (non-interactive): CI=true npm test -- --watchAll=false
- Docker
  - Build image: docker build -t virtuallab .
  - Run container (set env at runtime):
    - docker run -p 3000:80 \
        -e REACT_APP_API_URL=/api/v1 \
        -e BACKEND_API_URL=http://backend-api:8080/api/v1 \
        virtuallab
  - Local all-in-one stack: docker compose -f docker-compose.local.yml up -d --build
  - UAT all-in-one stack: docker compose --env-file .env.uat -f docker-compose.uat.yml up -d --build

Environment variables
- Local development: define in a .env file or export in shell before npm start
  - REACT_APP_API_URL
  - REACT_APP_LTI_API_URL
  - REACT_APP_AAD_CLIENT_ID
  - REACT_APP_AAD_AUTHORITY
  - REACT_APP_MAPS_API (optional)
- Container runtime: docker-entrypoint.sh replaces placeholders in built JS using the variables above, allowing runtime configuration without rebuilding.

High-level architecture
- Entry and providers
  - src/index.jsx creates the React root, wraps BrowserRouter with MsalProvider and LTIProvider, then renders <App />.
  - src/env.js reads runtime values from window.__ENV first, then build-time Vite env values.
- Routing
  - src/App.js defines routes for /, /home, /results, /courses, /courses/:courseShortCode, /module/:moduleID, /app (LTI entry), /dashboard, /lti-required, /callback, and a fallback.
  - src/pages/AppEntry.jsx implements the LTI flow: removes login_code from the URL, atomically exchanges it through ${LTI_API_URL}/lti/session/exchange, stores tab-scoped session/API tokens, then navigates to /home or /lti-required.
- Application shell
  - src/pages/AppLayout.js is the main layout (headlessui, heroicons) providing sidebar/topbar, dark mode toggle, and a profile menu. It renders children routes inside the main content area.
- Data access and state
  - src/pages/Home.js uses process.env.REACT_APP_API_URL with axios to call backend endpoints (e.g., /test-cors, /student-id/{email}, /students/, /students/logins), and stores identifiers and user metadata in sessionStorage.
  - Components under src/components/ provide UI elements and domain features (e.g., 3D viewer with three/react-three-fiber, forms, markdown rendering, course modules).
- 3D assets
  - public/draco contains Draco decoders for three.js; when using THREE.DRACOLoader, setDecoderPath to the decoders location under public.
- Testing setup
  - src/setupTests.js includes @testing-library/jest-dom; tests run with Jest via react-scripts.

Container serving and Nginx
- Dockerfile builds the app with node:22-alpine, then serves /build via nginx:alpine. It copies nginx.conf and docker-entrypoint.sh.
- nginx.conf
  - SPA routing: try_files $uri $uri/ /index.html;
  - Caching headers for static assets; basic security headers; /health endpoint returns 200.
- docker-entrypoint.sh
  - Replaces REACT_APP_* placeholders in built JS with environment variable values, then execs Nginx.

Notes
- There is no standalone lint script in package.json.
- No CLAUDE, Cursor, or Copilot instruction files were found.
