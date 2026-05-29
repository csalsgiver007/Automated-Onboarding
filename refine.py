import time
import sys
import os
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableClient

# This silences the noisy Azure SDK internal logs
import logging
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

# --- PRODUCTION CONFIGURATION ---
# The endpoint for your storage account tables
ACCOUNT_URL = "https://lumonstorage.table.core.windows.net/"
UNREFINED_TABLE = "UnrefinedStorage"
BINS = {"1": "Bin01", "2": "Bin02", "3": "Bin03", "4": "Bin04"}

# ANSI Color Codes for the "Severed" look
G = "\033[1;32m" # Lumon Green
B = "\033[1;34m" # Lumon Blue
Y = "\033[1;33m" # Warning Yellow
W = "\033[0m"    # Reset

def clear_screen():
    """Clears the terminal screen based on the OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_severed_name():
    """
    Formats the name in the 'Mark S.' style. 
    REFINER_NAME will be injected via environment variable by the Logic App.
    """
    full_name = os.getenv("REFINER_NAME", "Refiner Name")
    parts = full_name.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1][0]}."
    return full_name

def slow_print(text, speed=0.03):
    """Simulates the retro CRT terminal typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def print_header(name):
    """Prints the standardized Lumon header."""
    print(f"{G}====================================================")
    print(f"       LUMON INDUSTRIES - MACRODATA REFINEMENT      ")
    print(f"            TERMINAL ID: {name.upper()}-MDR             ")
    print(f"===================================================={W}\n")

def start_refinement():
    # Production Authentication: Uses Managed Identity (id-mdr-worker-prod)
    # when running in ACI, or your local Azure CLI login for testing.
    credential = DefaultAzureCredential()
    
    try:
        # Connect to the unrefined source
        source_client = TableClient(
            endpoint=ACCOUNT_URL, 
            table_name=UNREFINED_TABLE, 
            credential=credential
        )
        
        refiner_name = get_severed_name()
        
        clear_screen()
        print_header(refiner_name)
        
        slow_print(f"{B}Initializing encrypted connection to UnrefinedStore...{W}")
        entities = list(source_client.list_entities())
        
        if not entities:
            print(f"{Y}[!] No data clusters detected. Please contact your supervisor.{W}")
            return

        slow_print(f"{G}Connection established. Data clusters visualized.{W}\n")
        time.sleep(1)

        # Main Refinement Loop
        for entity in entities[:10]:
            val = entity.get("DataValue")
            
            clear_screen()
            print_header(refiner_name)
            
            print(f"{G}----------------------------------------------------")
            print(f" DATA CLUSTER: {W}{val}")
            print(f"{G}----------------------------------------------------{W}")
            
            print(f" [{B}1{W}] WO (Woe)    [{B}2{W}] FC (Frolic)")
            print(f" [{B}3{W}] DR (Dread)  [{B}4{W}] MA (Malice)")
            
            choice = ""
            while choice not in BINS:
                choice = input(f"\n{G}Identify dominant temper (1-4): {W}").strip()

            target_table = BINS[choice]
            target_client = TableClient(
                endpoint=ACCOUNT_URL, 
                table_name=target_table, 
                credential=credential
            )

            # Move data from unrefined to the specific bin
            target_client.create_entity({
                "PartitionKey": "Refined",
                "RowKey": entity['RowKey'],
                "DataValue": val
            })
            source_client.delete_entity(entity['PartitionKey'], entity['RowKey'])
            
            print(f"\n{B}>>> REFINEMENT SUCCESSFUL: {val} -> {target_table}{W}")
            time.sleep(0.8)

        # Completion UI
        clear_screen()
        print_header(refiner_name)
        print(f"\n{G}====================================================")
        slow_print("   QUOTA REACHED. YOU ARE VALUED. PRAISE KIER.   ")
        print(f"===================================================={W}")

    except Exception as e:
        print(f"{Y}CRITICAL ERROR: {e}{W}")

if __name__ == "__main__":
    start_refinement()