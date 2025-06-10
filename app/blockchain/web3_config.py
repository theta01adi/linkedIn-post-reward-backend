import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CONTRACT_ADDRESS = os.getenv("LINKEDIN_CONTRACT_ADDRESS")
OWNER_PUBLIC_ADDRESS = os.getenv("OWNER_PUBLIC_ADDRESS")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
WEB3_PROVIDER = os.getenv("ALCHEMY_PROVIDER")  
PINATA_JWT = os.getenv("PINATA_JWT")