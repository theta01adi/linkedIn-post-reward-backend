from web3 import Web3 
from app.blockchain.web3_config import WEB3_PROVIDER, LINKEDIN_CONTRACT_ADDRESS
from .contract_abi_loader import linkedin_contract_abi


def get_web3_instance():
    web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

    if not web3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum provider")
    
    return web3

def get_contract_instance():

    web3 = get_web3_instance()

    contract_instance = web3.eth.contract(address=Web3.to_checksum_address(LINKEDIN_CONTRACT_ADDRESS), abi=linkedin_contract_abi)

    return contract_instance