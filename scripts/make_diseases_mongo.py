import csv
import ast
import sys

# Povećaj limit za maksimalnu veličinu polja
csv.field_size_limit(sys.maxsize)

# Ulazni fajl
input_file = "diseases2.csv"
output_file = "diseases_mongo.csv"

unique_diseases = set()

with open(input_file, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        diseases_str = row["diseases"].strip()
        if diseases_str:
            try:
                diseases_list = ast.literal_eval(diseases_str)
                for disease in diseases_list:
                    unique_diseases.add(disease.strip())
            except Exception as e:
                print(f"Greška kod parsiranja: {diseases_str} ({e})")

sorted_diseases = sorted(unique_diseases)

with open(output_file, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["DiseaseId", "DiseaseName"])
    writer.writeheader()

    for idx, disease in enumerate(sorted_diseases, start=1):
        writer.writerow({
            "DiseaseId": idx,
            "DiseaseName": disease
        })

print(f"Gotov fajl: {output_file}")
