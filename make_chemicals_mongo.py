import csv
import ast
import sys

csv.field_size_limit(sys.maxsize)

# Ulazni fajlovi
merged_file = "merged_us2.csv"
diseases_file = "diseases2.csv"
diseases_map_file = "diseases_mongo.csv"

# Izlazni fajl
output_file = "chemicals_mongo.csv"

# 1. Učitaj DiseaseName -> DiseaseId mapu
disease_name_to_id = {}
with open(diseases_map_file, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        disease_name_to_id[row["DiseaseName"].strip()] = int(row["DiseaseId"])

# 2. Učitaj hemikalija -> lista bolesti (DiseaseName) iz diseases2.csv
chemical_to_diseases = {}
with open(diseases_file, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        chem_name = row["chemical"].strip()
        diseases_str = row["diseases"].strip()
        if diseases_str:
            try:
                diseases_list = ast.literal_eval(diseases_str)
                cleaned = [d.strip() for d in diseases_list]
                chemical_to_diseases[chem_name] = cleaned
            except Exception as e:
                print(f"Greška pri parsiranju bolesti za {chem_name}: {e}")

# 3. Prođi kroz merged_us2.csv i formiraj chemical entitete
unique_chemicals = {}
with open(merged_file, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        chem_id = row["39. TRI CHEMICAL/COMPOUND ID"].strip()
        chem_name = row["37. CHEMICAL"].strip()

        if chem_id not in unique_chemicals:
            unique_chemicals[chem_id] = {
                "ChemicalId": chem_id,
                "ChemicalName": chem_name,
                "UnitOfMeasure": "Grams",
                "PFAS": row["48. PFAS"].strip(),
                "PBT": row["47. PBT"].strip(),
                "Carcinogen": row["46. CARCINOGEN"].strip(),
                "Diseases": []
            }

# 4. Dodaj bolesti u Chemicals
for chem_name, diseases in chemical_to_diseases.items():
    # pronađi hemiju po imenu
    for chem in unique_chemicals.values():
        if chem["ChemicalName"].lower() == chem_name.lower():
            disease_ids = []
            for d in diseases:
                disease_id = disease_name_to_id.get(d)
                if disease_id:
                    disease_ids.append(disease_id)
            chem["Diseases"] = sorted(set(disease_ids))

# 5. Snimi u output CSV
with open(output_file, mode="w", encoding="utf-8", newline="") as f:
    fieldnames = ["ChemicalId", "ChemicalName", "UnitOfMeasure", "PFAS", "PBT", "Carcinogen", "Diseases"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for chem in unique_chemicals.values():
        writer.writerow({
            "ChemicalId": chem["ChemicalId"],
            "ChemicalName": chem["ChemicalName"],
            "UnitOfMeasure": chem["UnitOfMeasure"],
            "PFAS": chem["PFAS"],
            "PBT": chem["PBT"],
            "Carcinogen": chem["Carcinogen"],
            "Diseases": chem["Diseases"] if chem["Diseases"] else "[]"
        })

print(f"Gotov fajl: {output_file} ({len(unique_chemicals)} hemikalija)")
