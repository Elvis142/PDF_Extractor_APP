# Deploying Your Alcoa PDF Flask App to Render.com

## What's Integrated

Your custom Alcoa packing list processing is now fully integrated! The app:
- Extracts pkg_bundle, lot/job numbers, quantities, and weights from Alcoa PDFs
- Uses regex pattern matching to find: `BUNDLE LOT/JOB QTY PC WEIGHT_LB LB/WEIGHT_KG KG`
- Parses bundle and lot numbers to extract the relevant portions
- Returns structured CSV with: pkg_bundle, Lot/Job Num, Qty Ship, UOM, Net Weight (LB), Net Weight (KG)

## Step 1: Prepare Your GitHub Repository

1. Create a new repository on GitHub (go to github.com and click "New Repository")
   - Name it something like `alcoa-pdf-processor`
   - Leave it public for easier setup
   - Don't initialize with README

2. On your computer, navigate to your project folder in terminal/command prompt

3. Copy all the deployment files to your project folder:
   - app.py
   - index.html
   - requirements.txt
   - Procfile
   - render.yaml

4. Initialize Git and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Alcoa PDF processor with web interface"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/alcoa-pdf-processor.git
   git push -u origin main
   ```

5. Verify all files are on GitHub by viewing your repository in the browser

## Step 2: Deploy on Render.com

1. Go to https://render.com and sign up (you can use your GitHub account)

2. After signing in, click "New" → "Web Service"

3. Choose "Build and deploy from a Git repository"

4. Select "Connect account" next to GitHub and authorize Render to access your repos

5. Select your `alcoa-pdf-processor` repository

6. Fill in the deployment settings:
   - **Name**: `alcoa-pdf-processor` (or whatever you want)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (for testing)

7. Click "Create Web Service"

8. Render will now build and deploy your app (watch the logs). This takes 2-5 minutes.

## Step 3: Access Your Live App

Once deployment is complete (you'll see a green checkmark), you'll get a public URL like:
```
https://alcoa-pdf-processor.onrender.com
```

Share this link to use your app from anywhere!

## Step 4: Using Your Live App

1. **Upload PDFs**: Click the upload area or drag-and-drop Alcoa packing list PDFs
2. **Processing**: The app extracts data using your custom regex pattern
3. **Download**: Click "Download CSV" to get the structured data
4. **Manage**: Delete processed files from the list

## How It Works

**Regex Pattern** (matches Alcoa packing list format):
```
(\S+)\s+(\S+)\s+(\d+\.\d{2})\s+PC\s+(\d+)\s+LB/(\d+)\s+KG
```

This captures:
- Group 1: Package bundle
- Group 2: Lot/Job number
- Group 3: Quantity (decimal)
- Group 4: Weight in LB (integer)
- Group 5: Weight in KG (integer)

**Output CSV Columns**:
- pkg_bundle
- Lot/Job Num
- Qty Ship
- UOM (always "PC")
- Net Weight (LB)
- Net Weight (KG)

## Troubleshooting

**"No valid data found" error**:
- Check if the PDF format matches the expected pattern
- The regex looks for specific formatting: `BUNDLE LOT/JOB QTY PC WEIGHT_LB LB/WEIGHT_KG KG`
- Test locally first with a known-good Alcoa PDF

**App won't deploy**:
- Check the build logs on Render for error messages
- Make sure all files are in your GitHub repo
- Verify Python version compatibility

**App crashes after upload**:
- Check logs in Render dashboard
- May indicate PDF format issue or parsing error
- Test the PDF locally with your original script

**File storage note**:
- Render's free tier uses ephemeral storage
- Uploaded files are deleted after app restart (typically 15 minutes of inactivity)
- Consider upgrading plan for persistent storage if needed

## Making Changes

To update the regex pattern or processing logic:

1. Edit `app.py` locally
2. Update the `process_pdf()` function as needed
3. Push to GitHub:
   ```bash
   git add app.py
   git commit -m "Update PDF processing logic"
   git push
   ```
4. Render will automatically re-deploy with changes

## Next Steps

- Monitor your app performance in the Render dashboard
- Share the live URL with your team for testing
- Collect feedback on extracted data accuracy
- Update regex pattern if needed for different PDF layouts
- Consider upgrading storage for production use
