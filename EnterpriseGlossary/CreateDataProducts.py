"""
Sanitized CreateDataProducts script.

This file intentionally uses redacted placeholder values for product
metadata and credentials. It preserves the original create loop so the
script remains runnable (authentication will fail with the placeholder
credentials until real secrets are restored).
"""

from unifiedcatalogpy.client import UnifiedCatalogClient
from azure.identity import ClientSecretCredential


credential1 = ClientSecretCredential(
    tenant_id="1234", client_id="1234", client_secret="1234"
)

_client = UnifiedCatalogClient(account_id="1234", credential=credential1)


# Small, redacted list of data products. Fields that may contain
# sensitive or descriptive information have been replaced with
# placeholders per the user's sanitization request.
products = [
    {
        "name": "REDACTED_PRODUCT_1",
        "description": "REDACTED_DESCRIPTION_1",
        "status": "REDACTED_STATUS",
        "business_use": "REDACTED_BUSINESS_USE",
        "type": "REDACTED_TYPE",
        "governance_domain_id": "00000000-0000-0000-0000-000000000001",
        "owners": [{"id": "00000000-0000-0000-0000-000000000010"}],
    },
    {
        "name": "REDACTED_PRODUCT_2",
        "description": "REDACTED_DESCRIPTION_2",
        "status": "REDACTED_STATUS",
        "business_use": "REDACTED_BUSINESS_USE",
        "type": "REDACTED_TYPE",
        "governance_domain_id": "00000000-0000-0000-0000-000000000002",
        "owners": [{"id": "00000000-0000-0000-0000-000000000011"}],
    },
    {
        "name": "REDACTED_PRODUCT_3",
        "description": "REDACTED_DESCRIPTION_3",
        "status": "REDACTED_STATUS",
        "business_use": "REDACTED_BUSINESS_USE",
        "type": "REDACTED_TYPE",
        "governance_domain_id": "00000000-0000-0000-0000-000000000003",
        "owners": [{"id": "00000000-0000-0000-0000-000000000012"}],
    },
]


for product_data in products:
    # create_data_product will attempt to create the product in Purview.
    # With placeholder credentials/account this will not succeed; keep
    # the call in place so the script structure is preserved.
    product = _client.create_data_product(**product_data)
    print(product)
