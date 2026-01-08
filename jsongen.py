import requests
import csv
import json

# URL of the raw CSV file
url = "---"

# Fetch the CSV data
response = requests.get(url)
csv_text = response.text

# Read CSV into a list of dictionaries
lines = csv_text.splitlines()
reader = csv.DictReader(lines, fieldnames=["CarID", "NameFirstPart", "NameSecondPart", "Year"])
data = [row for row in reader]

# Save as JSON file
json_filename = "CarNames.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"JSON file saved as {json_filename}")
