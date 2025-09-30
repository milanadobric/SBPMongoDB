import csv
import json
from collections import defaultdict

# --- Učitavanje CSV fajlova ---
def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

onsite_release = read_csv("onsite_release_mongo.csv")
facilities = read_csv("reporting_facility_mongo.csv")
companies = read_csv("company_mongo.csv")
chemicals = read_csv("chemicals_mongo.csv")

# --- Kreiranje lookup mapa ---
facility_map = {f["FacilityId"]: f for f in facilities}
company_map = {c["CompanyId"]: c for c in companies}
chemical_map = {c["ChemicalId"]: c for c in chemicals}

# --- Grupisanje po (Year, FacilityId) ---
grouped = defaultdict(lambda: {"chemicals": defaultdict(lambda: {"releases": []})})

for row in onsite_release:
    year = int(row["Year"])
    fac_id = row["FacilityId"]
    chem_id = row["ChemicalId"]

    key = (year, fac_id)
    grouped[key]["year"] = year

    # Dodavanje release-a
    grouped[key]["chemicals"][chem_id]["releases"].append({
        "Air": float(row.get("Air") or 0),
        "Water": float(row.get("Water") or 0),
        "Underground": float(row.get("Underground") or 0),
        "Landfills": float(row.get("Landfills") or 0),
        "OnSiteReleaseTotal": float(row.get("OnSiteReleaseTotal") or 0),
        "OnSiteTreatmentTotal": float(row.get("OnSiteTreatmentTotal") or 0)
    })

    # Dodavanje hemikalije info
    chem_info = chemical_map.get(chem_id, {})
    grouped[key]["chemicals"][chem_id].update({
        "ChemicalName": chem_info.get("ChemicalName"),
        "PFAS": chem_info.get("PFAS"),
        "PBT": chem_info.get("PBT"),
        "Carcinogen": chem_info.get("Carcinogen"),
        "UnitOfMeasure": chem_info.get("UnitOfMeasure"),
        "Diseases": json.loads(chem_info.get("Diseases") or "[]")
    })

# --- Formiranje JSON objekata ---
output = []
count = 0

for (year, fac_id), fac_group in grouped.items():
    fac_data = facility_map.get(fac_id, {})
    parent_company_id = fac_data.get("ParentCompanyId")
    company_data = company_map.get(parent_company_id, {})

    obj = {
        "year": year,
        "facility": {
            "FacilityId": fac_id,
            "City": fac_data.get("City"),
            "State": fac_data.get("State"),
            "Latitude": float(fac_data.get("Latitude") or 0),
            "Longitude": float(fac_data.get("Longitude") or 0),
            "IndustrySector": fac_data.get("IndustrySector"),
            "Federal": (fac_data.get("FederalFacility","NO").upper() == "YES"),
            "ParentCompany": {
                "CompanyId": parent_company_id,
                "CompanyName": company_data.get("CompanyName") or company_data.get("StandardCompanyName")
            }
        },
        "allReleases": []
    }

    total_all_chemicals = 0.0
    for chem_id, chem_group in fac_group["chemicals"].items():
        total_releases_for_chemical = sum(r["OnSiteReleaseTotal"] for r in chem_group["releases"])
        total_all_chemicals += total_releases_for_chemical

        obj["allReleases"].append({
            "chemical": {
                "ChemicalId": chem_id,
                "ChemicalName": chem_group.get("ChemicalName"),
                "PFAS": chem_group.get("PFAS", "NO").upper() == "YES",
                "PBT": chem_group.get("PBT", "NO").upper() == "YES",
                "Carcinogen": chem_group.get("Carcinogen", "NO").upper() == "YES",
                "UnitOfMeasure": chem_group.get("UnitOfMeasure"),
                "diseases": chem_group.get("Diseases", []),
                "releasesForChemical": chem_group["releases"],
                "OnSiteReleaseTotalForChemical": total_releases_for_chemical
            }
        })

    obj["OnSiteReleaseTotalForAllChemicals"] = total_all_chemicals
    output.append(obj)
    count += 1
    if count % 100 == 0:
        print(f"Formirano JSON objekata: {count}")

# --- Upis u JSON fajl ---
with open("OnSiteReleaseAggregate.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Kraj! Ukupno objekata: {len(output)}")
