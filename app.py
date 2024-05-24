from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/api/posts', methods=['POST'])
def get_posts():
    # URL of the external API
    external_api_url = "https://redcap.h3abionet.org/redcap/api/"

    # Retrieve the API token from environment variables
    api_token = os.getenv('API_TOKEN')

    # Define headers including the authorization token
    data_header = {
        'token': {api_token},
        'content': 'report',
        'format': 'json',
        'report_id': '1065',
        'csvDelimiter': '',
        'rawOrLabel': 'label',
        'rawOrLabelHeaders': 'label',
        'exportCheckboxLabel': 'true',
        'returnFormat': 'json'
    }
    schema_header = {
        'token': {api_token},
        'content': 'metadata',
        'format': 'json',
        'returnFormat': 'json',
    }

    # Make a GET request to the external API with headers
    data_response = requests.get(external_api_url, headers=data_header)
    schema_response = requests.get(external_api_url, headers=schema_header)

    # Check if the request was successful
    if data_response.status_code == 200:
        # Get the JSON data from the response
        records = data_response.json()
        redcap_schema = schema_response.json()
    else:
        # If the request failed, return an error message
        return jsonify({"error": "Failed to retrieve data"}), data_response.status_code

    if schema_response.status_code == 200:
        # Get the JSON data from the response
        redcap_schema = schema_response.json()
    else:
        # If the request failed, return an error message
        return jsonify({"error": "Failed to retrieve schema"}), schema_response.status_code

    # Creates a list of project metadata fields in REDCap by examining project forms
    form_fields = []
    for record in redcap_schema:
        if record["form_name"] == "project_metadata":
            form_fields.append(record["field_name"])
        elif record["form_name"] == "contact_details":
            form_fields.append(record["field_name"])

    # Copies project metadata from project events to dataset events in REDCap using the list
    for record in records:
        if (record["redcap_event_name"] == "Project Info"):
            test_dict = {key: record[key] for key in form_fields}
        elif (record["redcap_event_name"] == "Dataset"):
            record.update(test_dict),
        else:
            break

    # Adds project acronyms if one does not already exist
    for record in records:
        if record["p_acronym"] == "":
            split_title = record["p_title"].split(":")
            record["p_acronym"] = split_title[0]

    # Splits the redcap json into projects and datasets for the catalogue to display
    projects = []
    datasets = []
    for record in records:
        if record["redcap_event_name"] == "Project Info":
            projects.append(record)
        elif record["redcap_event_name"] == "Dataset":
            datasets.append(record)
        else:
            break

    report = {
        "projects": projects,
        "datasets": datasets
    }
    return report


if __name__ == '__main__':
    app.run(debug=True)