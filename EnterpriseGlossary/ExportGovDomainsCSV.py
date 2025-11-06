from unifiedcatalogpy.client import UnifiedCatalogClient
from azure.identity import ClientSecretCredential
import csv
import re

# Set up credentials
credential1 = ClientSecretCredential(
    tenant_id="1234",
    client_id="1234",
    client_secret="1234"
)

# Initialize the Unified Catalog Client
_client = UnifiedCatalogClient(account_id="1234", credential=credential1)

# Get governance domains
domains = _client.get_governance_domains()

# Function to clean HTML tags
def clean_html(raw_html):
    return re.sub('<[^<]+?>', '', raw_html)

# Export to CSV
with open('governance_domains_cleaned.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Description'])  # Header
    for domain in domains:
        name = domain.get('name', '')
        raw_description = domain.get('description', '')
        cleaned_description = clean_html(raw_description)
        writer.writerow([name, cleaned_description])