# File Name : peterWork.py
# Student Name: Peter Phan
# email: phanpv@mail.uc.edu 
# Assignment Number: Assignment 11  
# Due Date:   4/17/25
# Course #/Section:   4010-001
# Semester/Year:   Spring 2025
# Brief Description of the assignment:  Clean up CSV data
# Brief Description of what this module does: This module just contains this single assignment
# Citations: Gemini: 

# Anything else that's relevant: N/A

import csv
import os
import requests

class DataCleaning:
    def __init__(self, input_csv_file, anomalies_csv_file, cleaned_csv_file, data_folder="Data"):
        self.input_csv_file = os.path.join(data_folder, input_csv_file)
        self.anomalies_csv_file = os.path.join(data_folder, anomalies_csv_file)
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def cleanup_data(self):
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
                fuel_type = row_dict.get('Fuel Type', '') # Use "Fuel Type"
                print(f"DEBUG (Cleanup): Row {row_number + 1}, Fuel Type: '{fuel_type}'") # Debugging line
                if fuel_type and 'pepsi' in fuel_type.strip().lower(): # Check "Fuel Type" for Pepsi
                    print(f"DEBUG (Cleanup): Pepsi found in row {row_number + 1}: {row}")
                    anomalies_data.append(row)
                    continue

                # Format Gross Price
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
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if header:
                writer.writerow(header)
            writer.writerows(data)

# --- modules/api_integration.py (Updated to extract City and State from "Full Address") ---
import csv
import os
import requests
import re # For extracting city and state

class ZipCodeUpdater:
    def __init__(self, cleaned_csv_file, updated_csv_file, data_folder="Data", api_url="https://app.zipcodebase.com/api/v1/search"):
        self.cleaned_csv_file = os.path.join(data_folder, cleaned_csv_file)
        self.updated_csv_file = os.path.join(data_folder, updated_csv_file) # Corrected line
        self.data_folder = data_folder
        self.api_url = api_url
        # Replace with your actual API key
        self.api_key = "219f52c0-162b-11f0-9537-61faffb5ee8d"

    def update_missing_zipcodes(self, max_updates=5):
        updated_data = []
        header = None
        zipcode_cache = {}
        updates_performed = 0

        with open(self.cleaned_csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            header = reader.fieldnames
            for row_number, row in enumerate(reader):
                full_address = row.get('Full Address', '')
                zipcode_match = re.search(r'(\d{5}(-\d{4})?)$', full_address) # Try to extract existing zip
                zipcode = zipcode_match.group(1) if zipcode_match else ''

                city = self._extract_city(full_address)
                state = self._extract_state(full_address)

                print(f"DEBUG (Zip): Row {row_number + 1}, Full Address: '{full_address}', City: '{city}', State: '{state}', ZipCode: '{zipcode}'") # Debugging

                if not zipcode and city and state and updates_performed < max_updates:
                    if (city, state) in zipcode_cache:
                        if 'ZipCode' not in row:
                            row['ZipCode'] = zipcode_cache[(city, state)]
                            header = list(header) + ['ZipCode'] # Update header
                        else:
                            row['ZipCode'] = zipcode_cache[(city, state)]
                        updates_performed += 1
                        print(f"DEBUG (Zip): Zip code found in cache for {city}, {state}: {row.get('ZipCode')}")
                    else:
                        zip_code = self._get_zipcode_from_api(city, state)
                        if zip_code:
                            if 'ZipCode' not in row:
                                row['ZipCode'] = zip_code
                                header = list(header) + ['ZipCode'] # Update header
                            else:
                                row['ZipCode'] = zip_code
                            zipcode_cache[(city, state)] = zip_code
                            updates_performed += 1
                            print(f"DEBUG (Zip): Updated zip code for {city}, {state}: {zip_code}")
                        else:
                            print(f"DEBUG (Zip): Failed to retrieve zip code for {city}, {state}")
                updated_data.append(row)

        output_filepath = self.updated_csv_file # Corrected line: Use the attribute directly
        with open(output_filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(updated_data)

    def _extract_city(self, address):
        city_match = re.search(r'([^,]+),', address)
        return city_match.group(1).strip() if city_match else None

    def _extract_state(self, address):
        state_match = re.search(r',\s*([A-Z]{2})\s*\d{5}(-\d{4})?$', address)
        if not state_match:
            state_match = re.search(r',\s*([A-Z]{2})$', address) # Try if no zip
        return state_match.group(1).strip() if state_match else None

    def _get_zipcode_from_api(self, city, state):
        if not self.api_key:
            print("Error: ZIP Code API key is missing. Cannot fetch zip codes.")
            return None
        params = {
            'apikey': self.api_key,
            'city': city,
            'country': 'US',
            'state': state
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            print(f"API Response for {city}, {state}: {data}") # Print raw response
            if data and 'results' in data and data['results']:
                first_result = next(iter(data['results'].values()))
                if first_result and 'postal_code' in first_result[0]:
                    return first_result[0]['postal_code']
            else:
                print(f"Warning: No valid zip code found in API response for {city}, {state}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error during API request for {city}, {state}: {e}")
            return None
        except ValueError as e:
            print(f"Error decoding JSON response for {city}, {state}: {e}")
            return None