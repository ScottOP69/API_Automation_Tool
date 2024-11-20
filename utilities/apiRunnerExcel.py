import json
import requests
import pandas as pd
import logging
import time

def get_responses(master_file, save_loc, db):
    # Configure the logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load the master test data workbook
    master_data = pd.ExcelFile(master_file)

    # Load the Parent Sheet to get microservice details
    parent_sheet = master_data.parse('Parent Sheet')

    # Use a session to persist cookies and headers across requests
    session = requests.Session()

    # Lists to be utilized to log execution details
    run_microservices = []
    response_time_arr = []

    # Iterate over each microservice in the Parent Sheet
    for _, service_row in parent_sheet.iterrows():
        microservice_name = service_row['Microservice Name']
        flag = service_row['Flag']
        base_url = service_row['Request URL']
        scenario_control = service_row['Scenario']

        if flag:  # Execute only if the flag is True
            # Append the microservice to the list of executed services
            run_microservices.append(microservice_name)
            logging.info(f"\nStarting execution for microservice: {microservice_name}")

            # Load the corresponding microservice sheet
            service_data = master_data.parse(microservice_name)

            # Initialize lists to store responses for different scenarios
            valid_responses = []
            invalid_responses = []
            null_responses = []

            # Take the start time for execution of the microservice
            start_time = time.time()

            # Filter data based on the scenario control from the Parent Sheet
            scenarios_to_run = ['Valid', 'Invalid', 'Null'] if scenario_control == 'All' else [scenario_control]

            # Iterate through each endpoint in the microservice sheet
            for _, endpoint_row in service_data.iterrows():
                endpoint_name = endpoint_row['Endpoint Name']
                endpoint_url = endpoint_row['Endpoint URL']
                method = endpoint_row['Method']

                # Construct the full request URL
                request_url = base_url + endpoint_url

                # Filter rows for scenarios to execute
                endpoint_scenarios = service_data[(service_data['Endpoint Name'] == endpoint_name) &
                                                  (service_data['Scenario'].isin(scenarios_to_run))]

                # Iterate through each scenario
                for _, scenario_row in endpoint_scenarios.iterrows():
                    scenario = scenario_row['Scenario']
                    request_body = scenario_row['Request Body']

                    # Initialize response variables
                    response = None

                    try:
                        # Send the request based on the method
                        if method == "GET":
                            response = session.get(request_url)
                        elif method in ['POST', 'PUT']:
                            if request_body and not pd.isna(request_body):
                                response = session.request(method, request_url, json=json.loads(request_body))
                            else:
                                response = session.request(method, request_url)

                        # Capture the status code and response text
                        if response:
                            status_code = response.status_code
                            response_text = response.json()
                        else:
                            status_code = "No Response"
                            response_text = "No Response"

                        # Log the response
                        response_time = response.elapsed.total_seconds()
                        logging.info(f"Request: {endpoint_name} | Scenario: {scenario} | ResponseTime: {response_time}s")

                        # Prepare result
                        result = {
                            'Endpoint Name': endpoint_name,
                            'Scenario': scenario,
                            'Status Code': status_code,
                            'Response': response_text
                        }

                        # Append the response to the corresponding scenario list
                        if scenario == "Valid":
                            valid_responses.append(result)
                        elif scenario == "Invalid":
                            invalid_responses.append(result)
                        elif scenario == "Null":
                            null_responses.append(result)

                    except Exception as e:
                        # Handle exceptions
                        result = {
                            'Endpoint Name': endpoint_name,
                            'Scenario': scenario,
                            'Status Code': "Error",
                            'Response': str(e)
                        }
                        if scenario == "Valid":
                            valid_responses.append(result)
                        elif scenario == "Invalid":
                            invalid_responses.append(result)
                        elif scenario == "Null":
                            null_responses.append(result)

            # Get the response time
            end_time = time.time()
            response_time = end_time - start_time
            response_time_arr.append(response_time)

            # Export results based on the scenario control
            if scenario_control == "All":
                pd.DataFrame(valid_responses).to_excel(f"{save_loc}{microservice_name}_Valid.xlsx", index=False)
                pd.DataFrame(invalid_responses).to_excel(f"{save_loc}{microservice_name}_Invalid.xlsx", index=False)
                pd.DataFrame(null_responses).to_excel(f"{save_loc}{microservice_name}_Null.xlsx", index=False)
            else:
                if scenario_control == "Valid":
                    pd.DataFrame(valid_responses).to_excel(f"{save_loc}{microservice_name}_Valid.xlsx", index=False)
                elif scenario_control == "Invalid":
                    pd.DataFrame(invalid_responses).to_excel(f"{save_loc}{microservice_name}_Invalid.xlsx", index=False)
                elif scenario_control == "Null":
                    pd.DataFrame(null_responses).to_excel(f"{save_loc}{microservice_name}_Null.xlsx", index=False)

            print(f"{microservice_name} | Reports Generated.")

    # Log the execution summary
    print("\n----------------------------------------")
    for service, res_time in zip(run_microservices, response_time_arr):
        print(f"Responses captured for {service} | Total time: {res_time}s")
    total_time = sum(response_time_arr)
    print(f"\nAbove responses from {db} server have been captured in {total_time} seconds.")
