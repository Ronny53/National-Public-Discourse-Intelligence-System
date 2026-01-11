# How to Set Up Email Alerts for NIS

This guide will help you configure the Email Alert System to send automatic and manual email notifications when high-risk situations are detected.

## Step 1: Choose Your Email Provider

The system is configured to work with **Gmail** by default, but you can use any SMTP-compatible email service. This guide focuses on Gmail setup.

**Supported Providers:**
- Gmail (recommended for this setup)
- Outlook/Hotmail
- Yahoo Mail
- Custom SMTP servers

## Step 2: Enable 2-Step Verification (Gmail)

Gmail requires App Passwords for SMTP access. To enable this:

1. **Go to your Google Account settings:**
   - Visit: [https://myaccount.google.com/security](https://myaccount.google.com/security)
   - Or: Click your profile picture → **Manage your Google Account** → **Security**

2. **Enable 2-Step Verification:**
   - Scroll to **"How you sign in to Google"** section
   - Click on **"2-Step Verification"**
   - Follow the prompts to set it up (you'll need your phone)
   - Complete the verification process

**Note:** You must enable 2-Step Verification before you can generate an App Password.

## Step 3: Generate a Gmail App Password

1. **Go back to Security settings:**
   - Visit: [https://myaccount.google.com/security](https://myaccount.google.com/security)
   - Navigate to **"2-Step Verification"** section

2. **Generate App Password:**
   - Scroll down to **"App passwords"** (you'll see this only after enabling 2-Step Verification)
   - Click on **"App passwords"**
   - You may need to sign in again

3. **Create the App Password:**
   - **Select app**: Choose **"Mail"** from the dropdown
   - **Select device**: Choose **"Other (Custom name)"**
   - **Enter name**: Type `NIS Email Alerts` (or any name you prefer)
   - Click **"Generate"**

4. **Copy the App Password:**
   - Google will show you a **16-character password** (with spaces, like: `abcd efgh ijkl mnop`)
   - **Copy this password** - you'll need it in the next step
   - **Important:** Remove the spaces when using it (it becomes: `abcdefghijklmnop`)
   - You won't be able to see this password again, so save it securely

## Step 4: Prepare Recipient Email Addresses

Decide who should receive the email alerts. You can add multiple recipients.

**Example recipients:**
- `recipient1@email.com`
- `recipient2@email.com`
- `admin@yourdomain.com`

**Note:** For this demo/academic project, recipients are treated as sub-branch/demo contacts, not official authorities.

## Step 5: Create or Update the .env File

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create or edit the `.env` file** (note the dot at the beginning)

   On Windows (PowerShell):
   ```powershell
   New-Item -Path .env -ItemType File -Force
   ```

   On Windows (Command Prompt):
   ```cmd
   type nul > .env
   ```

   On Mac/Linux:
   ```bash
   touch .env
   ```

3. **Open the `.env` file in a text editor** and add your email configuration:

   ```env
   # Email Alert Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_APP_PASSWORD=your_app_password_here
   EMAIL_RECIPIENTS=["recipient1@email.com","recipient2@email.com"]
   ALERT_THRESHOLD=70
   ALERT_COOLDOWN_MINUTES=15
   ```

   **Important:**
   - Replace `your_email@gmail.com` with your Gmail address (the one you used to generate the App Password)
   - Replace `your_app_password_here` with the 16-character App Password from Step 3 (remove spaces)
   - Replace the recipient emails with actual email addresses (keep the JSON array format with quotes)
   - `ALERT_THRESHOLD=70` means alerts trigger when risk score exceeds 70 (0-100 scale)
   - `ALERT_COOLDOWN_MINUTES=15` prevents sending duplicate alerts within 15 minutes

   **Example:**
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=vegarun999@gmail.com
   EMAIL_APP_PASSWORD=pobrbbkgjqsckfzy
   EMAIL_RECIPIENTS=["shreyashbamrara@gmail.com","vegarun666@gmail.com"]
   ALERT_THRESHOLD=70
   ALERT_COOLDOWN_MINUTES=15
   ```

4. **Save the file**

## Step 6: Alternative Email Providers

If you're not using Gmail, update the SMTP settings:

### Outlook/Hotmail:
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USER=your_email@outlook.com
EMAIL_APP_PASSWORD=your_app_password
```

### Yahoo Mail:
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USER=your_email@yahoo.com
EMAIL_APP_PASSWORD=your_app_password
```

### Custom SMTP:
```env
EMAIL_HOST=your.smtp.server.com
EMAIL_PORT=587
EMAIL_USER=your_email@domain.com
EMAIL_APP_PASSWORD=your_password
```

## Step 7: Verify the Setup

1. **Make sure the `.env` file is in the `backend/` directory** (or root directory - both work)

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
   - Look for any error messages about email configuration
   - If you see database initialization messages, the server started successfully

## Step 8: Test Email Configuration

1. **Log in to the frontend:**
   - Go to: `http://localhost:5173`
   - Log in with admin credentials:
     - Email: `admin@nis.gov.in`
     - Password: `admin123`

2. **Navigate to the Alerts tab:**
   - Click on **"Alerts"** in the navigation bar (only visible to admin users)

3. **Check Email Configuration Status:**
   - Look at the **"Email Configuration"** section
   - If configured correctly, you'll see: **"✓ Configured"** (green)
   - If not configured, you'll see: **"✗ Not configured"** (red)

4. **Send a Test Email:**
   - Click the **"Test Email"** button
   - Check your recipient email inboxes
   - You should receive a test email within a few seconds
   - If successful, you'll see a success message

## Step 9: Test Manual Alert

1. **Still on the Alerts page:**
   - Click the **"Send Alert Manually"** button
   - This will send an alert email with the current risk score
   - Check recipient inboxes for the alert email

2. **Verify Email Content:**
   - Subject: `[ALERT] High Risk Detected – NIS System`
   - Body should include:
     - Timestamp
     - Risk Score
     - Risk Category
     - Brief explanation
     - Footer disclaimer

## Step 10: Understand Automatic Alerts

Automatic alerts are sent when:
- The escalation risk score exceeds the threshold (default: 70)
- The dashboard refresh pipeline runs
- The cooldown period has passed (default: 15 minutes)

**How it works:**
- The system continuously monitors risk scores
- When risk score > threshold, an email is automatically sent
- Subsequent alerts are blocked for the cooldown period to prevent spam
- You can see the last alert time and cooldown status on the Alerts page

## Troubleshooting

### Problem: "Email configuration incomplete" or "Not configured"
**Solution:**
- Make sure the `.env` file exists in `backend/` directory (or root directory)
- Check that all required fields are filled:
  - `EMAIL_HOST`
  - `EMAIL_PORT`
  - `EMAIL_USER`
  - `EMAIL_APP_PASSWORD`
  - `EMAIL_RECIPIENTS`
- Verify there are no extra spaces around the `=` sign
- Make sure `EMAIL_RECIPIENTS` is in JSON array format: `["email1@example.com","email2@example.com"]`
- Restart the backend server after creating/modifying the `.env` file

### Problem: "Failed to send test email" or "Failed to send alert email"
**Solution:**
- Verify your App Password is correct (not your regular Gmail password)
- Make sure 2-Step Verification is enabled on your Google Account
- Check that the App Password doesn't have spaces (remove them if present)
- Verify `EMAIL_USER` matches the Gmail account used to generate the App Password
- Check your internet connection
- Try generating a new App Password and updating `.env`

### Problem: "SMTP Authentication failed"
**Solution:**
- Double-check your App Password (copy-paste it again)
- Make sure you're using an App Password, not your regular password
- Verify 2-Step Verification is enabled
- For Gmail, ensure "Less secure app access" is not the issue (App Passwords bypass this)

### Problem: "Recipients not receiving emails"
**Solution:**
- Check spam/junk folders
- Verify recipient email addresses are correct in `EMAIL_RECIPIENTS`
- Make sure the JSON array format is correct: `["email1@example.com","email2@example.com"]`
- Check backend console logs for specific error messages
- Try sending a test email first to verify configuration

### Problem: "Alert cooldown active"
**Solution:**
- This is normal behavior - alerts are rate-limited to prevent spam
- Wait for the cooldown period (default: 15 minutes) to expire
- You can see the remaining time on the Alerts page
- To change the cooldown, update `ALERT_COOLDOWN_MINUTES` in `.env` and restart server

### Problem: Emails going to spam
**Solution:**
- This is common for automated emails
- Ask recipients to mark emails as "Not Spam"
- Add sender email to contacts/whitelist
- For production, you'd use a professional email service (SendGrid, Mailgun, etc.)

## Important Notes

- **Keep your credentials private**: Never commit the `.env` file to Git (it's already in `.gitignore`)
- **App Password vs Regular Password**: Always use App Password for Gmail, never your regular password
- **Admin-only access**: Only users with admin role can access the Alerts tab and send manual alerts
- **Academic/Demo purposes**: This system is for educational use. Recipients are treated as demo contacts, not official authorities
- **Rate limiting**: Cooldown periods prevent alert spam. Automatic alerts respect the cooldown
- **Email format**: Recipients must be in JSON array format: `["email1@example.com","email2@example.com"]`

## Configuration Options

You can customize these settings in `.env`:

- **ALERT_THRESHOLD**: Risk score threshold for auto-alerts (default: 70, range: 0-100)
- **ALERT_COOLDOWN_MINUTES**: Minimum time between alerts (default: 15 minutes)
- **EMAIL_PORT**: SMTP port (587 for TLS, 465 for SSL, 25 for unencrypted)
- **EMAIL_HOST**: SMTP server address

## Still Having Issues?

1. Double-check all steps above, especially Step 3 (App Password generation)
2. Verify your `.env` file format is correct:
   - No extra spaces around `=`
   - JSON array format for recipients
   - No quotes around individual values (except in JSON arrays)
3. Restart your backend server after any `.env` changes
4. Check the backend console logs for specific error messages
5. Try the "Test Email" button first before testing manual alerts
6. Verify you're logged in as admin (`admin@nis.gov.in`) to access the Alerts tab

## Security Best Practices

- **Never share your App Password**: Treat it like your regular password
- **Rotate App Passwords**: Generate new ones periodically
- **Use separate App Passwords**: Create different ones for different applications
- **Monitor email activity**: Check your Google Account security page for suspicious activity
- **Limit recipients**: Only add trusted email addresses to `EMAIL_RECIPIENTS`
