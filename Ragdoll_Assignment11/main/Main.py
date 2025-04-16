# File Name : main.py
# Student Name: Peyton Bock
# email:  bockps@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   4/17/25
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Clean up CSV data
# Brief Description of what this module does: This module orchestrates the data cleaning, zip code updating, validation, and enhancement processes.
# Citations:
# - From peterWork.py and peytonWork.py
# - [https://app.zipcodebase.com/api/v1/code/city](https://app.zipcodebase.com/api/v1/code/city) (for API usage)

# Anything else that's relevant: N/A

from peterWorkPackage.peterWork import DataCleaning, ZipCodeUpdater
from peytonWorkPackage.peytonWork import DataValidator, DataEnhancer

INPUT_FILE = "fuelPurchaseData.csv"
ANOMALIES_FILE = "dataAnomalies.csv"
CLEANED_FILE = "cleanedData.csv"
UPDATED_FILE = "cleanedData.csv" # Overwrite cleanedData.csv with updated zips
VALIDATED_FILE = "validatedData.csv"
ENHANCED_FILE = "enhancedData.csv"
DATA_FOLDER = "Data"

if __name__ == "__main__":
    # Perform initial data cleaning
    data_cleaner = DataCleaning(INPUT_FILE, ANOMALIES_FILE, CLEANED_FILE, data_folder=DATA_FOLDER)
    data_cleaner.cleanup_data()
    print(f"Cleaned data written to Data/{CLEANED_FILE}")
    print(f"Anomalous data (Pepsi purchases) written to Data/{ANOMALIES_FILE}")

    # Update missing zip codes using the API for the first 5 rows
    zip_updater = ZipCodeUpdater(CLEANED_FILE, UPDATED_FILE, data_folder=DATA_FOLDER)
    zip_updater.update_missing_zipcodes(max_rows=5)
    print(f"Zip codes updated (first 5 missing) in Data/{UPDATED_FILE}")

    # Perform data validation
    data_validator = DataValidator(UPDATED_FILE, VALIDATED_FILE, data_folder=DATA_FOLDER)
    data_validator.validate_data()
    print(f"Data validation completed. Check Data/validation_issues.txt for details.")

    # Enhance the data
    data_enhancer = DataEnhancer(UPDATED_FILE, ENHANCED_FILE, data_folder=DATA_FOLDER)
    data_enhancer.enhance_data()
    print(f"Enhanced data written to Data/{ENHANCED_FILE}")
