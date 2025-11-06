CreateDataProducts usage

This file documents how to run `EnterpriseGlossary/CreateDataProducts.py`.

Prerequisites
- Python venv active and dependencies installed (see root README)
- `unifiedcatalogpy` and `azure-identity` available in the environment

Environment variables
- See `docs/CreateBusinessTerms.md` for example `.env` keys

Running the script

```powershell
C:/Users/xxx/Downloads/Scripts/.venv/Scripts/python.exe EnterpriseGlossary/CreateDataProducts.py
```

Notes
- The repository copy contains a redacted `products` list; fields that
  previously contained descriptive text have been replaced with
  placeholders (e.g. `REDACTED_PRODUCT_1`). Replace these with your
  intended product metadata if preparing to create data products in a
  non-production environment.
- The script will attempt to call `_client.create_data_product(...)`.
  With placeholder credentials the call will not succeed; ensure you
  supply valid credentials via environment variables or a secure
  secrets store.
