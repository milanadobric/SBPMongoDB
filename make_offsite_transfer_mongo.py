import csv
import sys

csv.field_size_limit(sys.maxsize)

# Konstanta za konverziju
POUND_TO_GRAMS = 453.59237

# Ulazni i izlazni fajlovi
input_file = "merged_us2.csv"
output_file = "offsite_transfer_mongo.csv"

# Kolone koje konvertujemo
numeric_columns = {
    "68. POTW - TOTAL TRANSFERS": "POTWTotalTransfers",
    "88. OFF-SITE RELEASE TOTAL": "OffSiteReleaseTotal",
    "94. OFF-SITE RECYCLED TOTAL": "OffSiteRecycledTotal",
    "97. OFF-SITE ENERGY RECOVERY T": "OffSiteEnergyRecoveryTotal",
    "104. OFF-SITE TREATED TOTAL": "OffSiteTreatedTotal",
    "106. 6.2 - TOTAL TRANSFER": "TotalTransfer",
    "118. 8.7 - TREATMENT OFF SITE": "TotalTreatmentIncludingPOTW"
}

with open(input_file, mode="r", encoding="utf-8", newline="") as f_in, \
     open(output_file, mode="w", encoding="utf-8", newline="") as f_out:

    reader = csv.DictReader(f_in)

    fieldnames = [
        "Year",
        "FacilityId",
        "ChemicalId",
        "POTWTotalTransfers",
        "OffSiteReleaseTotal",
        "OffSiteRecycledTotal",
        "OffSiteEnergyRecoveryTotal",
        "OffSiteTreatedTotal",
        "TotalTransfer",
        "TotalTreatmentIncludingPOTW"
    ]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            unit = row["50. UNIT OF MEASURE"].strip()
        except KeyError:
            unit = "Grams"

        multiplier = 1.0 if unit.lower() == "grams" else POUND_TO_GRAMS

        # Konvertuj vrednosti
        values = {}
        for src_col, dest_col in numeric_columns.items():
            try:
                val = float(row[src_col].replace(",", "").strip())
            except (ValueError, KeyError, AttributeError):
                val = 0.0
            values[dest_col] = val * multiplier

        writer.writerow({
            "Year": row["1. YEAR"].strip(),
            "FacilityId": row["2. TRIFD"].strip(),
            "ChemicalId": row["39. TRI CHEMICAL/COMPOUND ID"].strip(),
            "POTWTotalTransfers": values["POTWTotalTransfers"],
            "OffSiteReleaseTotal": values["OffSiteReleaseTotal"],
            "OffSiteRecycledTotal": values["OffSiteRecycledTotal"],
            "OffSiteEnergyRecoveryTotal": values["OffSiteEnergyRecoveryTotal"],
            "OffSiteTreatedTotal": values["OffSiteTreatedTotal"],
            "TotalTransfer": values["TotalTransfer"],
            "TotalTreatmentIncludingPOTW": values["TotalTreatmentIncludingPOTW"]
        })

print(f"Gotov fajl: {output_file}")
