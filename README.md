# Ride-Sharing ETL Data Pipeline

This project is a Python-based ETL data pipeline built to practice core data engineering concepts such as data extraction, cleaning, validation, transformation, rejected records handling, and loading clean data into SQL Server.

## Project Overview

The pipeline processes ride-sharing data from multiple file formats:

- `drivers.json`
- `rides.csv`
- `payments.txt`

The data is extracted, cleaned, validated, and then loaded into SQL Server tables. Invalid records are stored separately in a `rejected_data.json` file with clear rejection reasons.

## Tools & Technologies

- Python
- SQL Server
- SQL Server Management Studio (SSMS)
- pyodbc
- JSON
- CSV
- TXT files
- VS Code

## ETL Process

### 1. Extract

The pipeline extracts data from three different sources:

- Driver data from a JSON file
- Ride data from a CSV file
- Payment data from a TXT file

### 2. Transform

The transformation phase includes:

- Removing extra spaces
- Standardizing text format
- Converting data types
- Validating missing values
- Validating negative distances
- Validating invalid driver IDs
- Validating invalid ride IDs
- Filtering failed payments
- Handling incorrect data types

### 3. Load

Clean records are loaded into SQL Server tables:

- `drivers`
- `rides`
- `payments`

Rejected records are stored in:

- `rejected_data.json`

## Database Design

The project creates three relational tables:

### drivers

Stores valid driver information.

### rides

Stores valid ride records and references the `drivers` table using a foreign key.

### payments

Stores valid completed payments and references the `rides` table using a foreign key.

## Data Quality Handling

Invalid records are not ignored. They are stored in a separate JSON file with rejection reasons such as:

- Empty name
- Empty city
- Invalid distance
- Invalid driver ID
- Invalid ride ID
- Invalid payment status
- Value error

## Project Goal

The goal of this project is to practice building a simple but structured ETL pipeline similar to real-world data engineering workflows, where raw data is validated, cleaned, and loaded into a relational database.

## Future Improvements

- Add logging instead of print/debug outputs
- Move database configuration to environment variables
- Add SQL scripts in a separate folder
- Add more analytical queries
- Create a data flow diagram
- Add unit tests for validation rules
