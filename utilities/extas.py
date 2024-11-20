# Filter the test data for the current endpoint and selected scenarios
filtered_test_scenarios = test_scenarios[test_scenarios['Scenario'].isin(scenarios_to_run)]

# Iterate through only the filtered scenarios
for index, row in filtered_test_scenarios.iterrows():
    scenario = row['Scenario']  # This will now only contain scenarios in 'scenarios_to_run'
    request_body = row['Request Body']  # Test data for the scenario

    # Initialize the response variable
    response = None

    try:
        # Send the request based on the method
        if request_method == "GET":
            response = session.get(request_url)
        elif request_method in ['POST', 'PUT']:
            if request_body and not pd.isna(request_body):
                response = session.request(request_method, request_url, json=json.loads(request_body))
            else:
                response = session.request(request_method, request_url)

        # Capture the status code and response text
        if response:
            status_code = response.status_code
            response_text = response.json()
        else:
            status_code = "No Response"
            response_text = "No Response"

        # Log the response
        response_time = response.elapsed.total_seconds()
        logging.info(f"Request: {request_name} | Scenario: {scenario} | ResponseTime: {response_time}")

        # Append the response to the respective list
        result = {
            'Request Name': request_name,
            'Scenario': scenario,
            'Status Code': status_code,
            'Response': response_text
        }

        if scenario == "Valid":
            valid_responses.append(result)
        elif scenario == "Invalid":
            invalid_responses.append(result)
        elif scenario == "Null":
            null_responses.append(result)

    except Exception as e:
        # Handle errors and append the result to the respective list
        result = {
            'Request Name': request_name,
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
