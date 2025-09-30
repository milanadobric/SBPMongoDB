#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

input_file = "merged_us2.csv"
output_file = "company_mongo.csv"

# Kolone iz ulaznog CSV-a
parent_col = "15. PARENT CO NAME"
standard_col = "17. STANDARD PARENT CO NAME"

# Kolone u izlaznom CSV-u
output_fields = ["CompanyId", "CompanyName", "StandardCompanyName"]

def main():
    seen = set()  # skup za praćenje unikatnih CompanyName vrednosti
    company_id = 1

    with open(input_file, mode="r", encoding="utf-8", newline="") as infile, \
         open(output_file, mode="w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)

        # upiši header u izlazni fajl
        writer.writeheader()

        for row in reader:
            company_name = row.get(parent_col, "").strip()
            standard_name = row.get(standard_col, "").strip()

            # preskoči ako nema CompanyName
            if not company_name:
                continue

            # dodaj samo ako nije već viđen
            if company_name not in seen:
                seen.add(company_name)

                writer.writerow({
                    "CompanyId": company_id,
                    "CompanyName": company_name,
                    "StandardCompanyName": standard_name
                })
                company_id += 1

    print(f"✅ Gotovo! Izlazni fajl: {output_file}")

if __name__ == "__main__":
    main()
