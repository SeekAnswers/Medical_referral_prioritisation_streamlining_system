#  GitHub Token Setup for GitHub Models

## Current Issue
Your token needs the "models" permission but this checkbox isn't visible in the standard interface.

##  Try These Methods:

### Method 1: Fine-grained Personal Access Token (Recommended)
1. Go to: https://github.com/settings/personal-access-tokens/fine-grained
2. Click "Generate new token"
3. Choose "Fine-grained personal access token"
4. Set expiration (90 days recommended)
5. Under "Repository access" select "All repositories" or specific repo
6. In "Permissions" section, look for:
   - **"Models"** permission (if available)
   - **"Contents"** permission (read access)
   - **"Metadata"** permission (read access)

### Method 2: Classic Token with Broader Permissions
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select these scopes:
   -  **repo** (Full control of private repositories)
   -  **workflow** (Update GitHub Action workflows)
   -  **admin:repo_hook** (Full control of repository hooks)
   -  **user** (Update ALL user data)

### Method 3: Beta/Preview Access
GitHub Models might require beta access:
1. Visit: https://github.com/features/models
2. Sign up for preview access
3. Wait for approval email
4. Then generate token with "models" permission

##  Current Error Analysis
```
"The `models` permission is required to access this endpoint"
```

This suggests:
- Either the permission isn't available in your token interface yet
- Or GitHub Models requires special beta access
- Or we need to use a different authentication method

##  Immediate Alternatives

### Option A: Try Azure OpenAI Instead
If GitHub Models continues to have permission issues, we can use:
- Azure OpenAI with GPT-4
- Still free tier available
- Better medical performance than Groq

### Option B: Test with Broader Permissions
Create a classic token with ALL permissions temporarily to test:
- Go to classic token generation
- Select ALL checkboxes
- Test if this resolves the issue
- Then we can narrow down which specific permission is needed

##  Next Steps
1. Try Method 1 (Fine-grained) first
2. If no "models" permission visible, try Method 2 (All permissions)
3. If still issues, we'll switch to Azure OpenAI
4. Report back what permissions you see available
