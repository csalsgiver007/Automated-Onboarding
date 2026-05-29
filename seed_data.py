import uuid
import random
import os
import logging
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableClient
from azure.core.exceptions import AzureError

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_unrefined_data():
    """
    Seeds the Azure Table Storage using Managed Identity.
    """
    # The endpoint for your storage account tables
    ACCOUNT_URL = "https://lumonstorage.table.core.windows.net/"
    TABLE_NAME = "UnrefinedStorage"

    try:
        # Use Managed Identity/CLI credentials instead of a connection string
        credential = DefaultAzureCredential()
        
        client = TableClient(endpoint=ACCOUNT_URL, table_name=TABLE_NAME, credential=credential)
        
        with client:
            logger.info(f"Connected to {TABLE_NAME} via Identity. Starting seeding...")

            for i in range(1, 11):
                scary_number = random.randint(1000, 9999)
                entity = {
                    "PartitionKey": "MDR_Initial_Batch",
                    "RowKey": str(uuid.uuid4()),
                    "DataValue": scary_number,
                    "Status": "Unrefined"
                }
                client.create_entity(entity=entity)
            
            logger.info("[SUCCESS]: 10 clusters staged for refinement.")

    except AzureError as ae:
        logger.error(f"Azure Storage error: {ae.message}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    seed_unrefined_data()