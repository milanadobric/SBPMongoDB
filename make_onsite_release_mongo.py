import csv
import sys

csv.field_size_limit(sys.maxsize)

POUND_TO_GRAMS = 453.59237

input_file = "merged_us2.csv"
output_file = "onsite_release_mongo.csv"

with open(input_file, mode="r", encoding="utf-8", newline="") as f_in, \
     open(output_file, mode="w", encoding="utf-8", newline="") as f_out:

    reader = csv.DictReader(f_in)

    fieldnames = [
        "Year",
        "FacilityId",
        "ChemicalId",
        "Air",
        "Water",
        "Underground",
        "Landfills",
        "OnSiteReleaseTotal",
        "OnSiteTreatmentTotal"
    ]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        unit = row.get("50. UNIT OF MEASURE", "Grams").strip()
        multiplier = 1.0 if unit.lower() == "grams" else POUND_TO_GRAMS

        def safe_float(value):
            try:
                return float(value.replace(",", "").strip()) * multiplier
            except Exception:
                return 0.0

        fugitive_air = safe_float(row.get("51. 5.1 - FUGITIVE AIR", "0"))
        stack_air = safe_float(row.get("52. 5.2 - STACK AIR", "0"))
        air = fugitive_air + stack_air

        water = safe_float(row.get("53. 5.3 - WATER", "0"))

        underground = (
            safe_float(row.get("54. 5.4 - UNDERGROUND", "0")) +
            safe_float(row.get("55. 5.4.1 - UNDERGROUND CL I", "0")) +
            safe_float(row.get("56. 5.4.2 - UNDERGROUND C II-V", "0"))
        )

        landfills = (
            safe_float(row.get("57. 5.5.1 - LANDFILLS", "0")) +
            safe_float(row.get("58. 5.5.1A - RCRA C LANDFILL", "0")) +
            safe_float(row.get("59. 5.5.1B - OTHER LANDFILLS", "0"))
        )

        onsite_release_total = safe_float(row.get("65. ON-SITE RELEASE TOTAL", "0"))
        onsite_treatment_total = safe_float(row.get("117. 8.6 - TREATMENT ON SITE", "0"))

        writer.writerow({
            "Year": row.get("1. YEAR", "").strip(),
            "FacilityId": row.get("2. TRIFD", "").strip(),
            "ChemicalId": row.get("39. TRI CHEMICAL/COMPOUND ID", "").strip(),
            "Air": air,
            "Water": water,
            "Underground": underground,
            "Landfills": landfills,
            "OnSiteReleaseTotal": onsite_release_total,
            "OnSiteTreatmentTotal": onsite_treatment_total
        })

print(f"Gotov fajl: {output_file}")
