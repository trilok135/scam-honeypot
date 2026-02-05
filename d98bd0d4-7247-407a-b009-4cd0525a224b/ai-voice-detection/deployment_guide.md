
# Deployment Guide

## Option 1: Render.com (Recommended)
1. Fork/Clone this repo to GitHub/GitLab.
2. Sign up at [Render.com](https://render.com).
3. Click **New +** -> **Blueprints**.
4. Connect your repo.
5. Render will detect `render.yaml` and auto-configure.
6. **Important**: Go to Settings -> Environment Variables and set `API_KEY`.
7. Click **Apply**.

## Option 2: Docker
1. Build image:
   ```bash
   docker build -t voice-api .
   ```
2. Run container:
   ```bash
   docker run -p 8000:8000 -e API_KEY=your-secret voice-api
   ```

## Environment Variables
- `API_KEY`: Secret key for authentication.
- `PORT`: Port to run on (default 8000).
- `LOG_LEVEL`: Logging verbosity (default INFO).
