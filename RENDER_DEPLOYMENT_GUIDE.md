# Deploying Your PDF Flask App to Render.com

## Step 1: Prepare Your GitHub Repository

1. Create a new repository on GitHub (go to github.com and click "New Repository")
   - Name it something like `pdf-flask-app`
   - Leave it public for easier setup
   - Don't initialize with README

2. On your computer, navigate to your project folder in terminal/command prompt

3. Initialize Git and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: PDF Flask app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/pdf-flask-app.git
   git push -u origin main
   ```

4. Verify all files are on GitHub by viewing your repository in the browser

## Step 2: Deploy on Render.com

1. Go to https://render.com and sign up (you can use your GitHub account)

2. After signing in, click "New" → "Web Service"

3. Choose "Build and deploy from a Git repository"

4. Select "Connect account" next to GitHub and authorize Render to access your repos

5. Select your `pdf-flask-app` repository

6. Fill in the deployment settings:
   - **Name**: `pdf-flask-app` (or whatever you want)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (for testing)

7. Click "Create Web Service"

8. Render will now build and deploy your app (watch the logs)

## Step 3: Access Your Live App

Once deployment is complete (you'll see a green checkmark), you'll get a public URL like:
```
https://pdf-flask-app.onrender.com
```

Share this link to use your app from anywhere!

## Step 4: Update Your Custom PDF Processing

The `app.py` file has a placeholder `process_pdf()` function. You need to replace it with your actual PDF processing logic:

1. Open `app.py` in your editor
2. Find the `process_pdf(pdf_path)` function
3. Replace it with your custom script that extracts lot numbers, weights, and packing information
4. Push the changes to GitHub:
   ```bash
   git add app.py
   git commit -m "Update PDF processing logic"
   git push
   ```
5. Render will automatically re-deploy with your changes

## Example: Updating PDF Processing

Your custom function should:
- Take a file path as input
- Extract the data you need from the PDF
- Return a list of dictionaries (each dict is a row in the CSV)

Example format:
```python
def process_pdf(pdf_path):
    data = []
    # Your extraction logic here
    data.append({
        'lot_number': '12345',
        'weight': '500 lbs',
        'date': '2025-11-11',
        'description': 'Alcoa packing'
    })
    return data
```

## Troubleshooting

**App won't deploy:**
- Check the build logs on Render for error messages
- Make sure all files (Procfile, requirements.txt, etc.) are in your GitHub repo
- Verify Python version in render.yaml

**App crashes after deployment:**
- Check logs in Render dashboard
- Make sure your custom `process_pdf()` function doesn't have errors
- Test locally first before pushing changes

**Uploads not working:**
- Render uses ephemeral storage (files are deleted after restart)
- Consider using environment variables for file paths
- For permanent storage, upgrade to a paid Render plan

## Next Steps

- Monitor your app in the Render dashboard
- Share the live URL with your team
- Update the PDF processing logic to match your exact requirements
- Consider scaling up if you get heavy usage
