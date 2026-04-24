# Google Prototype Quickstart

This guide is intentionally minimal so you can deploy quickly.

## What is already wired in code

- Backend scan now generates an optional Gemini summary.
- If `GEMINI_API_KEY` is missing, scan still works and returns a non-fatal message.
- Session APIs return persisted `ai_summary` data.
- Dashboard renders the Gemini summary card when present.
- Frontend can use `VITE_API_BASE_URL` for deployed API URL.

## 1) Configure backend secrets

Create `.env` from `.env.example` in project root and set:

- `GEMINI_API_KEY`
- Optional: `GEMINI_MODEL` (default already set to `gemini-2.5-flash-lite`)

## 2) Deploy backend to Cloud Run

```bash
# from repo root
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud run deploy faircheck-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash-lite \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

Notes:

- Create secret first if needed:

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

If secret exists, add a new version:

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
```

## 3) Configure frontend API URL

Create `web/.env` from `web/.env.example` and set:

- `VITE_API_BASE_URL=https://YOUR_CLOUD_RUN_URL/api/v1`

## 4) Deploy frontend (Firebase Hosting)

```bash
cd web
npm install
npm run build
npm install -g firebase-tools
firebase login
firebase init hosting
# choose existing/new Firebase project, set public dir to dist, single-page app yes
firebase deploy
```

If `firebase init` already produced `firebase.json`, keep the current one if it matches your setup.

## 5) Verify demo flow

1. Open deployed frontend URL.
2. Upload model + dataset.
3. Confirm scan completes.
4. Confirm "Gemini Compliance Summary" card appears.

## 6) Cost guardrails (recommended)

- Keep Cloud Run `min-instances=0`.
- Set billing budget alerts in GCP.
- Keep Gemini model as `gemini-2.5-flash-lite` for lower cost.
