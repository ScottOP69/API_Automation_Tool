import json
import requests
import pandas as pd
import logging
import time
import os

def getResponses(collection_sheet, save_loc):
    # Configure the logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load the test data workbook
    test_data_file = ''  # Enter the test data file path
    test_data = pd.read_excel(test_data_file, sheet_name=None)

    # Load the Collections sheet to get collection file paths
    collections_sheet = test_data[collection_sheet]

    # Use a session to persist cookies and headers across requests
    session = requests.Session()

    # Iterate over each collection
    for _, collection_row in collections_sheet.iterrows():
        collection_name = collection_row['Collection Name']
        collection_file_path = collection_row['Collection File Path']
        flag = collection_row['Flag']
        scenario = collection_row['Scenario']
        reqUrl = collection_row['Request URL']

        if flag:
            logging.info(f"Starting collection: {collection_name} with Scenario: {scenario}")

            with open(collection_file_path, 'r') as file:
                postman_collection = json.load(file)

            requests_data = postman_collection['item']
            collection_test_data = test_data[collection_name]

            # Filter scenarios for 'Valid', 'Invalid', 'Null', or 'ALL'
            scenarios_to_run = ["Valid", "Invalid", "Null"] if scenario == "ALL" else [scenario]

            for current_scenario in scenarios_to_run:
                filtered_test_data = collection_test_data[collection_test_data['Scenario'] == current_scenario]
                responses = []

                start_time = time.time()

                for request in requests_data:
                    request_name = request['name']
                    request_url = request['request']['url']['raw'].replace("{{baseURL}}", reqUrl)
                    request_method = request['request']['method']

                    test_scenarios = filtered_test_data[filtered_test_data['Request Name'] == request_name]

                    for _, row in test_scenarios.iterrows():
                        scenario = row['Scenario']
                        request_body = row['Request Body']
                        response = None

                        try:
                            if request_method == "GET":
                                response = session.get(request_url)
                            elif request_method in ['POST', 'PUT']:
                                if request_body and not pd.isna(request_body):
                                    response = session.request(request_method, request_url, json=json.loads(request_body))
                                else:
                                    response = session.request(request_method, request_url)

                            response_time = response.elapsed.total_seconds() if response else 0
                            status_code = response.status_code if response else "No Response"
                            response_text = response.json() if response else "Request failed"

                            logging.info(f"Request: {request_name} | Scenario: {scenario} | Status: {status_code} | Time: {response_time:.2f}s")

                            result = {
                                'Request Name': request_name,
                                'Scenario': scenario,
                                'Status Code': status_code,
                                'Response': response_text,
                                'Response Time': response_time
                            }
                            responses.append(result)

                        except Exception as e:
                            logging.error(f"Error processing {request_name} ({scenario}): {str(e)}")

                end_time = time.time()
                total_time = end_time - start_time

                # Save responses to an Excel file
                responses_df = pd.DataFrame(responses)
                if scenario == "ALL":
                    output_file = os.path.join(save_loc, f'{collection_name}_{current_scenario}_Results.xlsx')
                else:
                    output_file = os.path.join(save_loc, f'{collection_name}_{scenario}_Results.xlsx')

                responses_df.to_excel(output_file, index=False)
                logging.info(f"Saved results to: {output_file} | Total Time: {total_time:.2f}s")

    logging.info("All collections processed successfully.")

















