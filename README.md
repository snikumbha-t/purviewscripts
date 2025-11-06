# Purview scripts

This repository contains a collection of Python scripts for working with
Azure Purview (Unified Data Catalog) and enterprise glossary/catalog
operations. The scripts automate common tasks such as creating business
terms, creating and managing data products, exporting and importing
governance domains, and other catalogue interactions.

IMPORTANT: This fork/snapshot has been sanitized for sharing. Credential
and account values have been replaced with placeholders (for example
"1234"). CSV files have been stripped of data rows and only contain
headers. Replace placeholders with real values in a secure manner (for
example via environment variables or an external secrets store) before
running any script against a live Purview instance.

Prerequisites
-------------
- Python 3.10+ (this repository was prepared with Python 3.12)
- A Python virtual environment for the project (recommended)
- Install required packages into the virtualenv:

```powershell
# from the workspace root
C:/Users/Downloads/Scripts/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

- The scripts use the `unifiedcatalogpy` client (and some scripts use
	`azure-purview-catalog` and `azure-identity`) for interacting with
	Purview. Install those packages if not already present:

```powershell
C:/Users/Downloads/Scripts/.venv/Scripts/python.exe -m pip install unifiedcatalogpy azure-purview-catalog azure-identity
```

Usage notes
-----------
- Many scripts expect credentials such as tenant id, client id and
	client secret. Do not hard-code secrets into these files. Use
	environment variables or a secrets manager. Example (PowerShell):

```powershell
$env:AZURE_TENANT_ID = "<your-tenant-id>"
$env:AZURE_CLIENT_ID = "<your-client-id>"
$env:AZURE_CLIENT_SECRET = "<your-client-secret>"
```

- Before pushing changes to a remote repo, make sure CSVs do not
	contain sensitive rows. This repository has been sanitized but
	double-check required files.

Index
-----
See `INDEX.md` for a short list of the most important scripts and their
purpose.

This repo contains scripts for interacting with Azure Purview. Credentials must be provided via environment variables or a secure secret store. DO NOT commit secrets.
