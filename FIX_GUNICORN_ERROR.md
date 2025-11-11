# Fixing: "bash: gunicorn: command not found"

## What You're Seeing
Your Render deployment failed with:
```
bash: line 1: gunicorn: command not found
Exited with status 127
```

This means gunicorn wasn't installed during the build process.

## Solution - Updated Files

I've fixed this with new versions of:
1. **requirements.txt** - Updated with compatible versions
2. **Procfile** - Fixed with proper PORT binding
3. **runtime.txt** - NEW - Specifies Python 3.11.7
4. **.gitignore** - NEW - Prevents unnecessary files from being deployed

## Step 1: Push Updated Files

Delete your old deployment and push these updated files:

```bash
# Make sure you have the new files in your local folder:
# - requirements.txt (updated)
# - Procfile (updated)
# - runtime.txt (new)
# - .gitignore (new)
# - app.py
# - index.html
# - render.yaml

git add .
git commit -m "Fix: Update deployment files with Python 3.11 support"
git push
```

## Step 2: Delete Failed Deployment

1. Go to your Render dashboard
2. Click on your service (alcoa-pdf-processor)
3. Go to "Settings" → scroll to bottom → "Delete Service"
4. Confirm deletion

## Step 3: Redeploy

1. Click "New" → "Web Service"
2. Select your GitHub repository again
3. This time it should work with the updated files!
4. Wait 5-10 minutes for the deployment to complete

## Why This Fix Works

**runtime.txt** - Tells Render exactly which Python version to use (3.11.7)
- Ensures compatibility with all packages
- Prevents version conflicts

**Updated Procfile** - Now includes proper PORT binding:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```
- The `$PORT` variable is required for Render
- `0.0.0.0` makes the app listen on all interfaces

**Updated requirements.txt** - Locked compatible versions:
- Flask 3.0.0
- gunicorn 21.2.0 (explicitly included)
- pdfplumber 0.10.3
- pandas 2.1.3
- pypdf 4.0.1
- Pillow 10.1.0

**.gitignore** - Prevents virtual environment from being deployed
- Render builds its own environment
- Deploying venv1/ causes issues

## If It Still Fails

Check the Render logs for new error messages:
1. Go to Render dashboard
2. Click your service
3. Scroll down to "Logs" section
4. Look for error details

Common issues:
- **"ModuleNotFoundError"** → Missing import in app.py
- **"SyntaxError"** → Python syntax issue in app.py
- **"ImportError: No module named 'pdfplumber'"** → pdfplumber didn't install (retry deployment)

## Alternative: Use a .env file (if needed)

If you need environment variables, create a `.env.example` file:

```bash
# .env.example (commit this to git)
FLASK_ENV=production
DEBUG=False
```

Then add actual values in Render dashboard:
Settings → Environment → Add environment variables

## Success Indicators

Once deployed successfully, you should see in Render logs:
```
Build successful ✓
==> Uploading build...
==> Deployed in X.Xs. Compression took X.Xs
==> Running 'gunicorn app:app --bind 0.0.0.0:$PORT'
```

Then your app URL will be live!
