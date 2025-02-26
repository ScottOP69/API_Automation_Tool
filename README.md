# API_Automation_Tool
![Framework](https://github.com/user-attachments/assets/4d417052-89f0-4f22-93e9-3d569e97726a)

# Overview

This tool is designed to simplify and automate the process of API testing and file comparison. Initially created to address a tight-schedule project where manual testing of endpoints was deemed necessary, this framework leverages Python and Beyond Compare software to save significant time and effort. It supports Excel-driven testing for API requests, compares database response times, and provides file comparison utilities.

# Features

# API Automation:

Automatically captures API response times for each endpoint and exports the data to an Excel file.

Compares response times between two databases (e.g., Sybase and SQL) and generates a detailed comparison report.

Allows users to run API tests either from Postman collections or directly from an Excel file containing endpoint details.

# File Comparison:

Compares files from two folders based on the given date, irrespective of file formats, using Beyond Compare.

# Excel-Driven Framework:

Enables users to input and manage API endpoint details, request payloads, and scenarios through an Excel file.

# Beyond Compare Integration:

Utilizes Beyond Compare for file and API response comparison.

# Customization:

Fully configurable using a config.ini file, allowing easy updates to variables and paths.

# Libraries Used

pandas: For manipulating and exporting data in Excel.

openpyxl: For reading and writing Excel files.

requests: For making API calls.

logging: For structured logging and debugging.

json: For parsing and handling JSON data.

shutil: For file operations.

configparser: For managing configuration files.

subprocess: For invoking Beyond Compare commands.

os: For file and directory management.

# Key Advantages

Time-Saving: Reduced a manual testing effort of 3 months to just 2 weeks.

Automation Despite Challenges: Developed under tight deadlines and initial skepticism about automation feasibility.

Versatile Utility: Handles both API and file comparison tasks seamlessly.

# Prerequisites

Python 3.x installed on your machine.

Beyond Compare software installed.

Required Python libraries installed (see the Installation section).

Input Excel files containing endpoint details and scenarios.

# Installation

Clone the repository:

git clone https://github.com/ScottOP69/API_Automation_Tool.git

Navigate to the project directory:

cd api-file-comparison-tool

Install the required Python libraries:

pip install -r requirements.txt



# Limitations

Beyond Compare must be installed separately.

File comparison only works on files present in the specified folders.



# Sample Master Test Data Sheet

<img width="959" alt="image" src="https://github.com/user-attachments/assets/e7d35fc1-7be9-4d48-aafe-982fe7dfbee9" />


# Sample Microservice Sheet

<img width="550" alt="microservice-data" src="https://github.com/user-attachments/assets/f5858a36-c11b-4def-b48d-3ea9a08d76d6" />


