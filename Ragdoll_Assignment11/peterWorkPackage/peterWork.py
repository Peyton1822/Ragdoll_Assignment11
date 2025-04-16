# File Name : peterWork.py
# Student Name: Peter Phan
# email: phanpv@mail.uc.edu
# Assignment Number: Assignment 11
# Due Date:   4/17/25
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Clean up CSV data
# Brief Description of what this module does: This module contains classes for initial data cleaning and updating missing zip codes using the zipcodebase.com API.
# Citations:
# - Gemini
# - [https://app.zipcodebase.com/api/v1/code/city](https://app.zipcodebase.com/api/v1/code/city) (for API usage)

# Anything else that's relevant: N/A

import csv
import os
import requests
import re

class DataCleaning:
    """
    A class to perform initial cleaning of the fuel purchase data.
    Tasks include:
    - Formatting Gross Price to 2 decimal places.
    - Removing duplicate rows.
    - Identifying and separating rows with 'Pepsi' purchases.
    """
    def __init__(self, input_csv_file, anomalies_csv_file, cleaned_csv_file, data_folder="Data"):
        """
        Initializes the DataCleaning object with input and output file paths.

        Args:
            input_csv_file (str): The path to the input CSV file.
            anomalies_csv_file (str): The path to the output CSV file for anomalous data.
            cleaned_csv_file (str): The path to the output cleaned CSV file.
            data_folder (str, optional): The folder containing the CSV files. Defaults to "Data".
        """
        self.input_csv_file = os.path.join(data_folder, input_csv_file)
        self.anomalies_csv_file = os.path.join(data_folder, anomalies_csv_file)
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def cleanup_data(self):
        """
        Performs the data cleaning operations: formatting prices, removing duplicates,
        and separating Pepsi purchases.
        """
        cleaned_data = []
        anomalies_data = []
        header = None
        processed_rows = set()

        with open(self.input_csv_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row_number, row in enumerate(reader):
                if not header:
                    header = row
                    cleaned_data.append(header)
                    continue

                row_tuple = tuple(row)
                if row_tuple in processed_rows:
                    print(f"DEBUG: Duplicate row found and skipped: {row}")
                    continue
                processed_rows.add(row_tuple)

                row_dict = dict(zip(header, row))
                fuel_type = row_dict.get('Fuel Type', '')
                print(f"DEBUG (Cleanup): Row {row_number + 1}, Fuel Type: '{fuel_type}'")
                if fuel_type and 'pepsi' in fuel_type.strip().lower():
                    print(f"DEBUG (Cleanup): Pepsi found in row {row_number + 1}: {row}")
                    anomalies_data.append(row)
                    continue

                gross_price = row_dict.get('Gross Price')
                if gross_price is not None:
                    try:
                        row_dict['Gross Price'] = f"{float(gross_price):.2f}"
                    except ValueError:
                        print(f"Warning: Could not format Gross Price for row: {row}")
                        continue

                cleaned_data.append(list(row_dict.values()))

        self._write_csv(self.cleaned_csv_file, cleaned_data)
        self._write_csv(self.anomalies_csv_file, anomalies_data, header=header)

    def _write_csv(self, filename, data, header=None):
        """
        Helper function to write data to a CSV file.

        Args:
            filename (str): The path to the output CSV file.
            data (list): The list of rows to write.
            header (list, optional): The header row. Defaults to None.
        """
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if header:
                writer.writerow(header)
            writer.writerows(data)

class ZipCodeUpdater:
    """
    A class to update missing zip codes in the cleaned data using the zipcodebase.com API.
    """
    def __init__(self, cleaned_csv_file, updated_csv_file, data_folder="Data", api_url="[https://app.zipcodebase.com/api/v1/code/city](https://app.zipcodebase.com/api/v1/code/city)"):
        """
        Initializes the ZipCodeUpdater object with input and output file paths and the API URL.

        Args:
            cleaned_csv_file (str): The path to the cleaned CSV file.
            updated_csv_file (str): The path to the output CSV file with updated zip codes.
            data_folder (str, optional): The folder containing the CSV files. Defaults to "Data".
            api_url (str, optional): The URL of the zip code API. Defaults to "[https://app.zipcodebase.com/api/v1/code/city](https://app.zipcodebase.com/api/v1/code/city)".
        """
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.updated_csv_file = os.path.join(data_folder, updated_csv_file)
        self.data_folder = data_folder
        self.api_url = api_url
        self.api_key = "219f52c0-162b-11f0-9537-61faffb5ee8d"
        self.zipcode_cache = {} # Cache to store fetched zip codes

    def update_missing_zipcodes(self, max_rows=None):
        """
        Updates missing zip codes for rows that lack them, up to a maximum number of rows.

        Args:
            max_rows (int, optional): The maximum number of rows to process for zip code updates.
                                       If None, process all rows.
        """
        updated_data = []
        header = None
        rows_processed = 0

        with open(self.cleaned_csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            header = reader.fieldnames
            for row_number, row in enumerate(reader):
                if max_rows is not None and rows_processed >= max_rows:
                    break  # Stop processing after max_rows

                full_address = row.get('Full Address', '')
                extracted_zip = self._extract_zip_from_address(full_address)
                extracted_city = self._extract_city_from_address(full_address)
                extracted_state = self._extract_state_from_address(full_address)

                print(f"DEBUG (Zip): Row {row_number + 1}, Full Address: '{full_address}', Extracted Zip: '{extracted_zip}', City: '{extracted_city}', State: '{extracted_state}'")

                if not extracted_zip and extracted_city and extracted_state:
                    cache_key = (extracted_city, extracted_state)
                    if cache_key in self.zipcode_cache:
                        zip_code = self.zipcode_cache[cache_key]
                        if 'ZipCode' not in row:
                            row['ZipCode'] = zip_code
                            header = list(header) + ['ZipCode']
                        else:
                            row['ZipCode'] = zip_code
                        print(f"DEBUG (Zip Cache): Zip code found in cache for {extracted_city}, {extracted_state}: {zip_code}")
                    else:
                        zip_code = self._get_zipcode_from_api(extracted_city, extracted_state)
                        if zip_code:
                            if 'ZipCode' not in row:
                                row['ZipCode'] = zip_code
                                header = list(header) + ['ZipCode']
                            else:
                                row['ZipCode'] = zip_code
                            self.zipcode_cache[cache_key] = zip_code
                            print(f"DEBUG (Zip API Success): Updated zip code for {extracted_city}, {extracted_state}: {zip_code}")
                        else:
                            print(f"DEBUG (Zip API Fail): Failed to retrieve zip code for {extracted_city}, {extracted_state}")

                updated_data.append(row)
                rows_processed += 1

        with open(self.updated_csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(updated_data)

    def _extract_zip_from_address(self, address):
        """
        Extracts a zip code (5 or 5+4 digits) from the address.
        """
        zip_match = re.search(r'(\d{5}(-\d{4})?)\b', address)
        return zip_match.group(1) if zip_match else None

    def _extract_state_from_address(self, address):
        """
        Extracts a two-letter uppercase state abbreviation from the address.
        """
        state_match = re.search(r'\b([A-Z]{2})\b', address)
        return state_match.group(1) if state_match else None

    def _extract_city_from_address(self, address):
        """
        Attempts to extract the city name from the address. This is a basic approach
        and might need refinement based on the specific format of the addresses.
        It looks for words followed by a comma.
        """
        city_match = re.search(r'([^,]+),', address)
        return city_match.group(1).strip() if city_match else None

    def _get_zipcode_from_api(self, city, state):
        """
        Calls the zipcodebase.com API to get zip codes for a given city and state using the /code/city endpoint.

        Args:
            city (str): The city name.
            state (str): The two-letter state abbreviation.

        Returns:
            str: The first zip code found by the API, or None if the API call fails or returns no results.
        """
        if not self.api_key:
            print("Error: ZIP Code API key is missing. Cannot fetch zip codes.")
            return None
        headers = {
            "apikey": self.api_key
        }
        params = {
            "city": city,
            "state_name": state, # Using 'state_name' as per the API example
            "country": "US"
        }
        print(f"DEBUG (API Request): URL: {self.api_url}, Headers: {headers}, Params: {params}") # Added debug
        try:
            response = requests.get(self.api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG (API Response): Raw API Response for {city}, {state}: {data}")
            if data and 'results' in data and data['results']:
                for result in data['results']:
                    if 'postal_code' in result:
                        print(f"DEBUG (API Success): Found zip code '{result['postal_code']}' for {city}, {state}")
                        return result['postal_code']
                print(f"Warning: No 'postal_code' found in API response results for {city}, {state}")
            else:
                print(f"Warning: No valid results found in API response for {city}, {state}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error during API request for {city}, {state}: {e}")
            return None
        except ValueError as e:
            print(f"Error decoding JSON response for {city}, state: {e}")
            return None