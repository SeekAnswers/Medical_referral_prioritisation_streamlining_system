# GitHub Models Setup Guide for Microsoft Phi-4-Reasoning (FREE)

### Quick Setup Steps

1. **Get GitHub Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   -  **IMPORTANT:** Select **"models"** permission (required for GitHub Models access)
   - Also select **"repo"** scope if needed
   - Copy your token

2. **Update Environment Variables:**
   ```bash
   # In your .env file, add:
   GITHUB_TOKEN=your_github_personal_access_token_here
   ```

3. **Verify Setup:**
   - Original Groq configuration is commented out (preserved)
   - New GitHub Models configuration is active
   - Model: `microsoft/phi-4-reasoning` (FREE during preview)

