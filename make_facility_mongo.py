#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

input_file = "merged_us2.csv"
companies_file = "company_mongo.csv"
output_file = "reporting_facility_mongo.csv"

# Kolone iz ulaznog CSV-a
columns = {
    "FacilityName": "4. FACILITY NAME",
    "City": "6. CITY",
    "State": "8. ST",
    "Latitude": "12. LATITUDE",
    "Longitude": "13. LONGITUDE",
    "ZIP": "9. ZIP",
    "County": "7. COUNTY",
    "IndustrySector": "23. INDUSTRY SECTOR",
    "FederalFacility": "21. FEDERAL FACILITY",
    "FacilityId": "2. TRIFD",   # ključ
    "EPAID": "3. FRS ID",
    "CompanyName": "15. PARENT CO NAME"  # za povezivanje
}

# Kolone u izlaznom CSV-u
output_fields = [
    "FacilityName", "City", "State", "Latitude", "Longitude",
    "ZIP", "County", "IndustrySector", "FederalFacility",
    "FacilityId", "EPAID", "ParentCompanyId"
]

def load_companies_map():
    """ Učitaj mapu CompanyName -> CompanyId iz company_mongo.csv """
    mapping = {}
    with open(companies_file, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["CompanyName"].strip()
            cid = row["CompanyId"].strip()
            if name:
                mapping[name] = cid
    return mapping

def main():
    seen = set()  # TRIFID set za uklanjanje duplikata
    company_map = load_companies_map()
    print(company_map)

    with open(input_file, mode="r", encoding="utf-8", newline="") as infile, \
         open(output_file, mode="w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            facility_id = row.get(columns["FacilityId"], "").strip()
            if not facility_id or facility_id in seen:
                continue
            seen.add(facility_id)

            # mapiraj ParentCompanyName -> ParentCompanyId
            company_name = row.get(columns["CompanyName"], "").strip()
            parent_id = company_map.get(company_name, "")

            # formiraj novi zapis
            new_row = {
                "FacilityName": row.get(columns["FacilityName"], "").strip(),
                "City": row.get(columns["City"], "").strip(),
                "State": row.get(columns["State"], "").strip(),
                "Latitude": row.get(columns["Latitude"], "").strip(),
                "Longitude": row.get(columns["Longitude"], "").strip(),
                "ZIP": row.get(columns["ZIP"], "").strip(),
                "County": row.get(columns["County"], "").strip(),
                "IndustrySector": row.get(columns["IndustrySector"], "").strip(),
                "FederalFacility": row.get(columns["FederalFacility"], "").strip(),
                "FacilityId": facility_id,
                "EPAID": row.get(columns["EPAID"], "").strip(),
                "ParentCompanyId": parent_id
            }

            writer.writerow(new_row)

    print(f"✅ Gotovo! Izlazni fajl: {output_file}")

if __name__ == "__main__":
    main()
