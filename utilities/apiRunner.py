import json
import requests
import pandas as pd
import logging
import time


def getResponses(collection_sheet, save_loc, db):
    # Configure the logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load the test data workbook
    test_data_file = ''  # Enter the Location
    test_data = pd.read_excel(test_data_file, sheet_name=None)

    # Load the Collections sheet to get Collection file paths
    collections_sheet = test_data[collection_sheet]

    # Use a session to persist cookies and headers across requests
    session = requests.Session()

    # Lists to be utilized to print out the ran collections and time taken
    run_collections = []
    response_time_arr = []

    # Iterate over each collection file path

    for _, collection_row in collections_sheet.iterrows():

        # Load all the Values from each column in the collection sheet
        collection_name = collection_row['Collection Name']  # Name of the Collection
        collection_file_path = collection_row['Collection File Path']  # Path of the Collection
        flag = collection_row['Flag']  # Boolean Flag
        reqUrl = collection_row['Request Url']  # Get the Base URL

        if flag:

            # Append the values into the list to be printed at the end
            run_collections.append(collection_name)
            # Display log for the current Collection
            logging.info(f"\nStarting to run collection : {collection_name}")

            # Load the Postman Collection with JSON
            with open(collection_file_path, 'r') as file:
                postman_collection = json.load(file)

            # Extract the requests from the collection
            requests_data = postman_collection['item']

            # Load the required test data for the collection
            collection_test_data = test_data[collection_name]

            # Initialize the lists to store responses for different scenarios
            valid_responses = []
            invalid_responses = []
            null_responses = []

            # Take the start time for execution of the Microservice
            start_time = time.time()

            # Iterate through each request in the Postman Collection
            for request in requests_data:
                request_name = request['name']
                request_url = request['request']['url']['raw']  # Traverse throught the JSON and fetch the URL
                baseUrl = reqUrl
                # Replace the BaseUrl Variables in the URL
                request_url = request_url.replace("{{baseURL}}", baseUrl)
                request_method = request['request']['method']

                # Fetch test data for the current session
                test_scenarios = collection_test_data[collection_test_data['Request name'] == request_name]

                # Iterate throught each scenario -> Valid, Invalid and Null

                for index, row in test_scenarios.iterrows():
                    scenario = row['Scenario']  # Column C in the master test data sheet
                    request_body = row['Request Body']  # Column D in the master test data sheet

                    # Initialize the response variables
                    response = None

                    try:

                        # Send the request based on the method
                        if(request_method) == "GET":
                            response = session.get(request_url)
                        elif request_method in ['POST','PUT']:
                            if request_body and not pd.isna(request_body):
                                response = session.request(request_method,request_url,json=json.load(request_body))
                            else:
                                response = session.request(request_method, request_url)

                        #Capture the status code and response text

                        if response:
                            status_code = response.status_code
                            response_text = response.json()
                        else:
                            status_code= response.status_code
                            response_text = response.json()
                            response_text = removeTimeStamp(response_text)

                        #Log the Response
                        response_time = response.elapsed.total_seconds()
                        logging.info(f"Request ; {request_name} | Scenario : {scenario} | ResponseTime : {response_time}")

                        #Append the response into respective lists
                        result ={
                            'Request Name': request_name,
                            'Scenario' : scenario,
                            'Satus Code' : status_code,
                            'Response' : response_text
                        }

                        if scenario == "Valid":
                            valid_responses.append(result)
                        elif scenario == "Invalid":
                            invalid_responses.append(result)
                        elif scenario=="Null":
                            null_responses.append(result)

                    except Exception as e:
                        result = {
                            'Request Name' : request_name,
                            'Scenario' : scenario,
                            'Status Code' : "Error",
                            'Response' : str(e)
                        }

                        if scenario == "Valid":
                            valid_responses.append(result)
                        elif scenario == "Invalid":
                            invalid_responses.append(result)
                        elif scenario=="Null":
                            null_responses.append(result)


            # Get the response times
            end_time = time.time()
            response_time = end_time-start_time
            response_time_arr.append(response_time)

            # Create Dataframes for each scenario
            valid_df = pd.DataFrame(valid_responses)
            invalid_df = pd.DataFrame(invalid_responses)
            null_df = pd.DataFrame(null_responses)

            # Export the result
            valid_df.to_excel(save_loc+collection_name+'_Valid.xlsx')
            invalid_df.to_excel(save_loc+collection_name+'_InValid.xlsx')
            null_df.to_excel(save_loc+collection_name+'_Null.xlsx')

            print(f'{collection_name} | Report Generated')

    print()
    print("----------------------------------------")
    for col,res_time in zip(run_collections,response_time_arr):
        print(f'Responses captured for {col} | Total time : {res_time}s')
    print()
    total_time = sum(response_time_arr)
    print(f'Above responses from {db} server have been captured in {total_time} seconds')


def removeTimeStamp(response_text):
    response = json.loads(response_text)
    response["timestamp"]=""
    return json.dumps(response,indent=4)
