import requests
import json
import csv
import os

BASE_URL = "https://integration.aberdeencity.gov.uk"
MAP_INTEGRATION_URL = BASE_URL + "/apibroker/runLookup?id=5ba25e5ed7042"
OUTPUT_PATH = "_data/roads.csv"

payload = json.dumps(
    {
        "formValues": {
            "Problem": {
                "problemCategoryTitle": {
                    "name": "problemCategoryTitle",
                    "type": "text",
                    "id": "AF-Field-7b5e73ad-ab1d-4900-b7d9-ebce86c2af2b",
                    "value_changed": True,
                    "section_id": "AF-Section-5ce840d2-da3a-45e4-abf9-de7bb9033f3f",
                    "label": "problemCategoryTitle",
                    "value_label": "",
                    "hasOther": False,
                    "value": "Road",
                    "path": "root/problemCategoryTitle",
                    "valid": True,
                    "totals": "",
                    "suffix": "",
                    "prefix": "",
                    "summary": "",
                    "hidden": False,
                    "_hidden": True,
                    "isSummary": False,
                    "staticMap": False,
                    "isMandatory": False,
                    "isRepeatable": False,
                    "currencyPrefix": "",
                    "decimalPlaces": "",
                    "hash": "",
                }
            }
        }
    }
)
headers = {
    "content-type": "application/json",
}

session = requests.Session()

session_cookie_init = session.request("GET", BASE_URL)

response = session.request("POST", MAP_INTEGRATION_URL, headers=headers, data=payload)

print(
    f"Got response with {response.status_code} and content length {str(len(response.content))}"
)

roads_data = response.json()["integration"]["transformed"]["rows_data"]

roads_data_count = len(roads_data)

print(f"Found {roads_data_count} reported road issues")

output_data = []

for problem in roads_data:
    print(problem)
    problem_data = problem.split(".")

    output_data_row = []

    problem_type = problem_data[0]

    problem_reported_date_string = problem_data[1]
    problem_reported_date = problem_reported_date_string.split(" ")[3]

    problem_primary_action_string = problem_data[2]
    problem_primary_action_split = problem_primary_action_string.strip().split(" ")
    problem_primary_action_type = (
        "Make safe"
        if problem_primary_action_split[2] == "safe"
        else problem_primary_action_split[1].capitalize()
    )
    problem_primary_action_date = problem_primary_action_split[-1]

    output_data_row.extend(
        [
            problem_type,
            problem_reported_date,
            problem_primary_action_type,
            problem_primary_action_date,
        ]
    )

    try:
        problem_assessment_status = problem_data[3].strip()
        output_data_row.append(problem_assessment_status)
    except IndexError:
        output_data_row.append(None)

    try:
        problem_repair_date_string = problem_data[4]
        problem_repair_date_split = problem_repair_date_string.strip().split(" ")
        output_data_row.append(problem_repair_date_split[-1])
    except IndexError:
        output_data_row.append(None)

    problem_metadata = roads_data[problem]

    problem_latitude = problem_metadata["lat"]
    problem_longitude = problem_metadata["lng"]
    problem_case_status = problem_metadata["status"]
    problem_last_updated = problem_metadata["lastUpdated"]

    output_data_row.extend([problem_latitude, problem_longitude, problem_case_status, problem_last_updated])

    output_data.append(output_data_row)
    # output_data.append(problem_data)

header = [
    "Problem type",
    "Reported date",
    "Primary action type",
    "Primary action date",
    "Assessment status",
    "Repair date",
    "Lat",
    "Lng",
    "Case status",
    "Last updated",
]

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", newline="") as f:
    csv_writer = csv.writer(f)

    csv_writer.writerow(header)

    csv_writer.writerows(output_data)
