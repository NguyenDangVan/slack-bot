from google.oauth2.credentials import Credentials

# Load the private key file
creds = Credentials.from_service_account_file("path/to/private_key.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
