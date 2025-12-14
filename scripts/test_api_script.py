#### #! DO NOT MODIFY THIS CODE #! ####

import requests

API_BASE_URL = "http://localhost:8000"

def test_api() -> dict:
    """
    Test the API by making a GET request to the test-view endpoint.

    :return: The JSON response from the test-view endpoint.
    :rtype: dict
    """
    response = requests.get(f"{API_BASE_URL}/app/test-view/")
    return response.json()


#### #! END OF DO NOT MODIFY THIS CODE #! ####

# Build your script here.

def get_chart_schema() -> dict:

    response = requests.get(f"{API_BASE_URL}/app/chart-schema/")
    return response.json()
    """
    Get the chart schema from the API.



    :return: The API response.
    :rtype: dict
    """
    pass

import json
def transform_chart_to_json() -> dict:
    """
    Transform the raw medical chart text file into a structured JSON object.

    :return: The JSON object of the transformed chart.
    :rtype: dict
    """
    chart_path = "data/medical_chart.txt"

    with open(chart_path, "r") as f:
        lines = [line.rstrip() for line in f]

    notes = []
    current_note_type = None
    current_note_id = None
    current_content_lines = []

    for line in lines:
        # Detect note headers (ALL CAPS, no colon)
        if line.isupper() and line.strip():
            # Save previous note if it exists
            if current_note_id:
                notes.append({
                    "note_type": current_note_type,
                    "note_id": current_note_id,
                    "content": " ".join(current_content_lines).strip()
                })
                current_content_lines = []

            current_note_type = line
            current_note_id = None

        # Detect note ID line
        elif line.startswith("Note ID:"):
            current_note_id = line.replace("Note ID:", "").strip()

        # Accumulate content
        elif current_note_id:
            if line.strip():  # ignore empty lines
                current_content_lines.append(line.strip())

    # Append last note
    if current_note_id:
        notes.append({
            "note_type": current_note_type,
            "note_id": current_note_id,
            "content": " ".join(current_content_lines).strip()
        })

    # Extract chart_id from any note_id (e.g., note-hpi-case12 → case12)
    chart_id = notes[0]["note_id"].split("-")[-1] if notes else "unknown"

    # Add chart_id to each note
    for note in notes:
        note["chart_id"] = chart_id

    return {
        "chart_id": chart_id,
        "notes": notes
    }

def upload_chart() -> dict:
    """
    Upload a chart to the API.

    :return: The API response.
    :rtype: dict
    """
    chart_json = transform_chart_to_json()
    response = requests.post(
        f"{API_BASE_URL}/app/upload-chart/",
        json=chart_json
    )
    return response.json()

def list_charts() -> dict:

    response = requests.get(
        f"{API_BASE_URL}/app/charts/"
    )

    return response.json()

    """
    List all the charts in the API.

    :return: The API response.
    :rtype: dict
    """

def code_chart() -> dict:
    """
    Code a chart using the API.

    :return: The API response.
    :rtype: dict
    """
    chart_json = transform_chart_to_json()
    response = requests.post(
        f"{API_BASE_URL}/app/code-chart/",
        json={"chart_id": chart_json["chart_id"]}
    )
    return response.json()


#### #! DO NOT MODIFY THIS CODE #! ####

def build_output() -> str:
    """
    Print the output of the script.
    """

    print("##### OUTPUT GENERATION #####")
    print()
    
    print("Test Output:")
    print()
    print(test_api())

    print()
    print("--------------------------------")
    print()

    print("1. Chart Schema:")
    print()
    print(get_chart_schema())

    print()
    print("--------------------------------")
    print()

    print("2. Chart to JSON:")
    print()
    print(transform_chart_to_json())

    print()
    print("--------------------------------")
    print()

    print("3. Upload Chart:")
    print()
    print(upload_chart())

    print()
    print("--------------------------------")
    print()

    print("4. List Charts:")
    print()
    print(list_charts())

    print()
    print("--------------------------------")
    print()

    print("5. Code Chart:")
    print()
    print(code_chart())

    print()
    print("--------------------------------")
    print()

    print("##### END OF OUTPUT GENERATION #####")

build_output()

#### #! END OF DO NOT MODIFY THIS CODE #! ####
