CreateBusinessTerms usage

This file documents how to run `EnterpriseGlossary/CreateBusinessTerms.py`.

Prerequisites
- Set up a Python virtual environment and install dependencies (see
  root README)
- Ensure `unifiedcatalogpy` and `azure-identity` are installed in the venv

Environment variables (example)

Create a `.env` file (or export variables in your shell) with the
following values. Do NOT commit `.env` to source control.

```text
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
PURVIEW_ACCOUNT_ID=your-purview-account-id
```

Running the script

```powershell
# Activate your venv, then
C:/Users/xxx/Downloads/Scripts/.venv/Scripts/python.exe EnterpriseGlossary/CreateBusinessTerms.py
```

Notes
- The script uses `unifiedcatalogpy.client.UnifiedCatalogClient` to
  interact with Purview. In the sanitized copy of the repo, credential
  placeholders like "1234" are used. Replace those with secure
  environment variables prior to running.
- This example demonstrates the expected environment and execution
  pattern; it will not run successfully until valid credentials and
  account values are provided.
