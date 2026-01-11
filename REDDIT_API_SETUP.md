# How to Get Real-Time Reddit Data for NIS

This guide will help you set up Reddit API credentials to fetch real data instead of synthetic data.

## Step 1: Create a Reddit Account (if you don't have one)

1. Go to [https://www.reddit.com](https://www.reddit.com)
2. Sign up for a free account if you don't already have one
3. Verify your email address if prompted

## Step 2: Create a Reddit Application

1. **Go to Reddit's App Preferences:**
   - Visit: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
   - Or: Click your profile → **User Settings** → Scroll down to **"Developed Applications"** section

2. **Create a New Application:**
   - Scroll to the bottom of the page
   - Click the **"create an app"** or **"create another app..."** button

3. **Fill in the Application Form:**
   - **Name**: `NIS Hackathon App` (or any name you prefer)
   - **App type**: Select **"script"** (important!)
   - **Description**: `National Public Discourse Intelligence System - Hackathon Project`
   - **About URL**: (leave blank or add your GitHub repo URL)
   - **Redirect URI**: `http://localhost:8000` (required field, even if unused)

4. **Click "create app"**

## Step 3: Get Your Credentials

After creating the app, you'll see your app listed. You need to find:

1. **Client ID** (also called "Personal use script"):
   - This is the **string of random characters** shown under your app's name
   - It looks like: `abc123xyz456def789`
   - This is your `REDDIT_CLIENT_ID`

2. **Secret** (also called "secret"):
   - Next to your app, there's a field labeled "secret"
   - Click on it or hover to reveal it
   - It looks like: `xyz789_ABC123-def456-GHI789`
   - This is your `REDDIT_CLIENT_SECRET`

## Step 4: Create the .env File

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a new file named `.env`** (note the dot at the beginning)

   On Windows (PowerShell):
   ```powershell
   New-Item -Path .env -ItemType File
   ```

   On Windows (Command Prompt):
   ```cmd
   type nul > .env
   ```

   On Mac/Linux:
   ```bash
   touch .env
   ```

3. **Open the `.env` file in a text editor** and add your credentials:

   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   REDDIT_USER_AGENT=python:nis.hackathon:v1.0.0 (by /u/YOUR_REDDIT_USERNAME)
   ```

   **Important:**
   - Replace `your_client_id_here` with your actual Client ID from Step 3
   - Replace `your_secret_here` with your actual Secret from Step 3
   - Replace `YOUR_REDDIT_USERNAME` with your Reddit username (the one you use to log in)

   **Example:**
   ```env
   REDDIT_CLIENT_ID=abc123xyz456def789
   REDDIT_CLIENT_SECRET=xyz789_ABC123-def456-GHI789
   REDDIT_USER_AGENT=python:nis.hackathon:v1.0.0 (by /u/john_doe)
   ```

4. **Save the file**

## Step 5: Verify the Setup

1. **Make sure the `.env` file is in the `backend/` directory** (not in the root directory)

2. **Restart your backend server:**
   - Stop the server if it's running (Ctrl+C)
   - Navigate to the root directory:
     ```bash
     cd ..
     ```
   - Start the server again:
     ```bash
     python -m uvicorn backend.api.main:app --reload
     ```

3. **Check the console output:**
   - If you see: `"Reddit API connection successful. Real data mode enabled."` → ✅ Success!
   - If you see: `"Reddit credentials missing or invalid. Using synthetic data mode."` → Check your `.env` file

## Step 6: Test Real Data Fetching

1. **Trigger a data refresh:**
   - Go to your frontend: `http://localhost:5173`
   - Log in to the dashboard
   - Click "Refresh" or wait for automatic refresh

2. **Check the backend logs:**
   - Look for messages like: `"Successfully fetched X real posts from r/india"`
   - This confirms real data is being fetched

## Troubleshooting

### Problem: "Reddit credentials missing or invalid"
**Solution:**
- Make sure the `.env` file is in the `backend/` directory
- Check that there are no extra spaces around the `=` sign
- Make sure you didn't include quotes around the values
- Verify the credentials are correct (copy-paste them again)

### Problem: "Failed to init Reddit client"
**Solution:**
- Verify your Client ID and Secret are correct
- Make sure your Reddit account email is verified
- Check your internet connection
- Try creating a new Reddit app and using those credentials

### Problem: "No posts retrieved"
**Solution:**
- This might happen if the subreddit has no recent posts
- The system will automatically fall back to synthetic data
- Try checking the logs for more details

### Problem: Rate Limiting
**Solution:**
- Reddit API has rate limits (60 requests per minute)
- The app is designed to handle this, but if you see rate limit errors, wait a minute and try again
- For production use, you'd need OAuth authentication (not implemented in this hackathon version)

## Important Notes

- **Keep your credentials private**: Never commit the `.env` file to Git (it's already in `.gitignore`)
- **Free tier limits**: Reddit's free API has rate limits but is sufficient for this project
- **No OAuth needed**: For this hackathon version, we use "script" type apps which don't require OAuth
- **Synthetic data fallback**: If Reddit API fails, the system automatically uses synthetic data so the app keeps working

## Still Having Issues?

1. Double-check all steps above
2. Make sure your `.env` file format is correct (no extra spaces, no quotes)
3. Restart your backend server after creating/modifying the `.env` file
4. Check the backend console logs for specific error messages
