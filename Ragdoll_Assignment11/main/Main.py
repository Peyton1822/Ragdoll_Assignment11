# File Name : main.py
# Student Name: Peyton Bock
# email:  bockps@mail.uc.edu
# Assignment Number: Assignment 11  
# Due Date:   4/17/25
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Clean up CSV data
# Brief Description of what this module does: This module just contains this single assignment
#Citations: 

# Anything else that's relevant: N/A

from peterWorkPackage.peterWork import DataCleaning
from peterWorkPackage.peterWork import ZipCodeUpdater

INPUT_FILE = "fuelPurchaseData.csv"
ANOMALIES_FILE = "dataAnomalies.csv"
CLEANED_FILE = "cleanedData.csv"
UPDATED_FILE = "cleanedData.csv" # Overwrite cleanedData.csv with updated zips
DATA_FOLDER = "Data"

if __name__ == "__main__":
    # Perform initial data cleaning
    data_cleaner = DataCleaning(INPUT_FILE, ANOMALIES_FILE, CLEANED_FILE, data_folder=DATA_FOLDER)
    data_cleaner.cleanup_data()
    print(f"Cleaned data written to Data/{CLEANED_FILE}")
    print(f"Anomalous data (Pepsi purchases) written to Data/{ANOMALIES_FILE}")

    # Update missing zip codes using the API
    zip_updater = ZipCodeUpdater(CLEANED_FILE, UPDATED_FILE, data_folder=DATA_FOLDER)
    zip_updater.update_missing_zipcodes()
    print(f"Zip codes updated (first 5 missing) in Data/{UPDATED_FILE}")


    #Peyton Work Area



    #End if statement

