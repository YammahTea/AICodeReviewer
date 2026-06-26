# codeReviewer

A GitHub App that automatically reviews pull requests using Google Gemini AI. When a PR is opened or updated, the bot analyzes the diff and posts a review comment.

---

## Project Structure

```
codeReviewer/
├── Back/
│   ├── prompts/
│   │   └── reviewer.md       # The prompt template sent to Gemini
│   ├── app.py                # FastAPI app, handles GitHub webhook events
│   ├── auth.py               # GitHub App JWT + installation token logic
│   └── comment.py            # Posts review comments back to GitHub
├── .env                      # Secrets (never commit this)
├── Dockerfile.lambda         # For AWS Lambda deployment
```

---

## Environment Setup

Create a `.env` file in the project root:

```env
APP_ID=123467
CLIENT_ID=SomeString
GEMINI_API_KEY=SomeRandomString
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAzcy2I81Rmb0w...\n-----END RSA PRIVATE KEY-----"
```

### How to get each variable

**`APP_ID` and `CLIENT_ID`**

1. Go to [github.com/settings/profile](https://github.com/settings/profile)
2. Scroll down on the right sidebar and click **Developer settings**
3. Click **GitHub Apps** then **New GitHub App**
3.1- Only fill in the App's name 
3.2- Scroll down to find `Homepage URL` section and fill it with this format: `https://github.com/{YOUR_GITHUB_USERNAME}`
4. After creating the app, click the **General** tab on the left
5. `APP_ID` and `CLIENT_ID` are listed below the **About** section

---

**Permissions & Events**

Before finishing app creation, configure the required permissions and webhook events under the **Permissions & Events** tab.


<img width="959" height="718" alt="githubApp_permissions" src="https://github.com/user-attachments/assets/0ed20956-4113-4ccc-a41a-dbfed6cbdc0f" />

---

**`GEMINI_API_KEY`**

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in and create a new API key

---

**`PRIVATE_KEY`**

1. In your GitHub App settings, click the **General** tab
2. Scroll down to **Private keys** and click **Generate a private key** - a `.pem` file will download automatically. Keep this file safe.
3. Open the `.pem` file in Notepad
4. At the end of each line, type `\n` then delete the actual line break, so the entire key becomes one line

Before:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAzcy2I81Rmb0wTHvUfCzhSN4xmXyHRi0V8eqB7Kr2nQJKaP7h
...
RT92Aayhh0pvde/lDS0WjbAb/wVCbydcd4beBHedQ+oDaOOAY0/bJg==
-----END RSA PRIVATE KEY-----
```

After (wrap the whole thing in double quotes):
```
"-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAzcy2I81Rmb0wTHvUfCzhSN4xmXyHRi0V8eqB7Kr2nQJKaP7h\n...\nRT92Aayhh0pvde/lDS0WjbAb/wVCbydcd4beBHedQ+oDaOOAY0/bJg==\n-----END RSA PRIVATE KEY-----"
```

---

## Running Locally (Docker)

Build and run the container from the project root:

```bash
docker build -t code-reviewer -f Back/Dockerfile .
docker run --env-file .env -p 8000:8000 code-reviewer
```

The app will be available at `http://localhost:8000`.

### Optional - Expose your local server for webhook testing (smee.io)

This lets GitHub send webhook events to your local machine during development.

1. Go to [smee.io](https://smee.io) and click **Start a new channel** - copy the URL it gives you
2. Set that URL as the **Webhook URL** in your GitHub App settings (under the General tab)
3. Install the smee client:
   ```bash
   npm install --global smee-client
   ```
4. Forward events to your local server:
   ```bash
   smee --url https://smee.io/your-channel-id --target http://localhost:8000
   ```

Now any PR event on a repo where your app is installed will be forwarded to your local container.

> For a 24/7 deployment, use the Lambda version below instead.

---

## AWS Lambda Deployment

Use `Dockerfile.lambda` for serverless deployment on AWS.

1. Build the image and push it to **AWS ECR** (Elastic Container Registry)
2. In the AWS Lambda console, create a new function from a **container image** and select the image you uploaded to ECR
3. Set the same `.env` variables as Lambda environment variables in the function's configuration
4. Use the Lambda function URL (or an API Gateway URL) as the **Webhook URL** in your GitHub App settings

---

## Notes

- The `mangum` library has no effect on the application logic - it is only used to make the app compatible with AWS Lambda's event format.
- You can configure the review prompt in `prompts/reviewer.md` to include more rules or extra functionality!
- Please star this repo if you found it useful :)
