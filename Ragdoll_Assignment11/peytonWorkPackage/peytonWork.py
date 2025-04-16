# File Name : peytonWork.py
# Student Name: Peyton Bock
# email:  bockps@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   4/17/25
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Clean up CSV data
# Brief Description of what this module does: This module contains classes for additional data cleaning tasks such as validation and enhancement.
# Citations:
# - [https://docs.python.org/3/library/csv.html](https://docs.python.org/3/library/csv.html)
# - [https://docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html)

import csv
import os
import re

class DataValidator:
    """
    A class to perform data validation checks on the cleaned fuel purchase data.
    """
    def __init__(self, cleaned_csv_file, validated_csv_file, data_folder="Data"):
        """
        Initializes the DataValidator with input and output file paths.

        Args:
            cleaned_csv_file (str): The path to the cleaned CSV file.
            validated_csv_file (str): The path to the output validated CSV file (currently used for logging).
            data_folder (str, optional): The folder containing the CSV files. Defaults to "Data".
        """
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.validated_csv_file = os.path.join(data_folder, validated_csv_file)
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def validate_data(self):
        """
        Performs data validation on the cleaned data, checking for potential issues.
        This includes:
        - Checking for valid date formats in the 'Transaction Date' column.
        - Checking for reasonable 'Gallons Purchased' values (non-negative).
        - Checking if 'Driver ID' is in a consistent format (alphanumeric).
        - Identifying potential outliers in 'Gross Price' or 'Gallons Purchased' (basic).

        Note: This method identifies potential issues and documents them in a log file.
        """
        validation_issues = []
        with open(self.cleaned_csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row_number, row in enumerate(reader):
                transaction_date = row.get('Transaction Date', '')
                if transaction_date and not re.match(r'^\d{4}-\d{2}-\d{2}', transaction_date):
                    validation_issues.append(f"Row {row_number + 2}: Invalid date format in 'Transaction Date': '{transaction_date}'")

                try:
                    gallons = float(row.get('Gallons Purchased', 0))
                    if gallons < 0:
                        validation_issues.append(f"Row {row_number + 2}: Negative value in 'Gallons Purchased': '{gallons}'")
                except ValueError:
                    validation_issues.append(f"Row {row_number + 2}: Non-numeric value in 'Gallons Purchased': '{row.get('Gallons Purchased')}'")

                driver_id = row.get('Driver ID', '')
                if driver_id and not re.match(r'^[a-zA-Z0-9]+$', driver_id):
                    validation_issues.append(f"Row {row_number + 2}: Potential issue with 'Driver ID' format: '{driver_id}'")

                try:
                    gross_price = float(row.get('Gross Price', 0))
                    if gross_price > 1000:  # Example outlier threshold
                        validation_issues.append(f"Row {row_number + 2}: Potential outlier in 'Gross Price': '{gross_price}'")
                    if gallons > 100:  # Example outlier threshold
                        validation_issues.append(f"Row {row_number + 2}: Potential outlier in 'Gallons Purchased': '{gallons}'")
                except ValueError:
                    pass

        if validation_issues:
            print("\n--- Potential Data Issues Found ---")
            for issue in validation_issues:
                print(issue)
            print("-----------------------------------\n")
            self._write_validation_log(validation_issues)
        else:
            print("\n--- Data validation complete: No obvious issues found based on defined checks. ---\n")
            self._write_validation_log([])

    def _write_validation_log(self, issues):
        """
        Writes the validation issues to a text file.

        Args:
            issues (list): A list of validation issue strings.
        """
        log_file = os.path.join(self.data_folder, "validation_issues.txt")
        with open(log_file, 'w') as f:
            if issues:
                f.write("--- Potential Data Issues Found ---\n")
                for issue in issues:
                    f.write(issue + "\n")
                f.write("-----------------------------------\n")
            else:
                f.write("--- Data validation complete: No obvious issues found based on defined checks. ---\n")
        print(f"Validation log written to: {log_file}")

class DataEnhancer:
    """
    A class to enhance the fuel purchase data by adding derived columns.
    This example adds a 'Price Per Gallon' column.
    """
    def __init__(self, cleaned_csv_file, enhanced_csv_file, data_folder="Data"):
        """
        Initializes the DataEnhancer with input and output file paths.

        Args:
            cleaned_csv_file (str): The path to the cleaned CSV file.
            enhanced_csv_file (str): The path to the output enhanced CSV file.
            data_folder (str, optional): The folder containing the CSV files. Defaults to "Data".
        """
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.enhanced_csv_file = os.path.join(data_folder, enhanced_csv_file)
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def enhance_data(self):
        """
        Enhances the data by adding a 'Price Per Gallon' column.
        """
        enhanced_data = []
        header = None
        with open(self.cleaned_csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            header = reader.fieldnames
            if header and 'Price Per Gallon' not in header:
                header = list(header) + ['Price Per Gallon']
            enhanced_data.append(header)
            for row in reader:
                try:
                    gross_price = float(row.get('Gross Price', 0))
                    gallons = float(row.get('Gallons Purchased', 0))
                    if gallons != 0:
                        price_per_gallon = f"{gross_price / gallons:.2f}"
                    else:
                        price_per_gallon = "N/A"
                    row['Price Per Gallon'] = price_per_gallon
                    enhanced_data.append(row)
                except ValueError:
                    row['Price Per Gallon'] = "Error"
                    enhanced_data.append(row)
                except ZeroDivisionError:
                    row['Price Per Gallon'] = "N/A"
                    enhanced_data.append(row)

        self._write_csv(self.enhanced_csv_file, enhanced_data, header=header)
        print(f"Enhanced data written to Data/{self.enhanced_csv_file}")

    def _write_csv(self, filename, data, header=None):
        """
        Helper function to write data to a CSV file.

        Args:
            filename (str): The path to the output CSV file.
            data (list): The list of data rows (dictionaries).
            header (list, optional): The header row. Defaults to None.
        """
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(data[1:]) # Write data rows