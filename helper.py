from google.cloud import secretmanager
from typing import Dict

def get_gcp_secrets(project_id: str = "kataros") -> Dict[str, str]:
    client = secretmanager.SecretManagerServiceClient()
    
    secrets = {}
    secret_ids = ["OPENAI_API_KEY", "PINECONE_API_KEY"]
    
    for secret_id in secret_ids:
        try:
            # Build the resource name
            name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            
            # Access the secret version
            response = client.access_secret_version(request={"name": name})
            
            # Decode payload
            secret_value = response.payload.data.decode("UTF-8")
            secrets[secret_id] = secret_value
            
        except Exception as e:
            print(f"Error accessing secret {secret_id}: {str(e)}")
    
    return secrets

# Usage
try:
    secrets = get_gcp_secrets()
    print(f"Found {len(secrets)} secrets")
    print(secrets)
except Exception as e:
    print(f"Error getting secrets: {e}")