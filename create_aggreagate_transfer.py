#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json

# ---- Učitavanje CSV fajlova ----
offsite_df = pd.read_csv("offsite_transfer_mongo.csv")
chemicals_df = pd.read_csv("chemicals_mongo.csv")
facilities_df = pd.read_csv("reporting_facility_mongo.csv")
companies_df = pd.read_csv("company_mongo.csv")

# Mapiranje hemikalija po ChemicalId
chemicals_map = chemicals_df.set_index("ChemicalId").to_dict(orient="index")

# Mapiranje kompanija po CompanyId
companies_map = companies_df.set_index("CompanyId").to_dict(orient="index")

# Mapiranje facility po FacilityId
facilities_map = facilities_df.set_index("FacilityId").to_dict(orient="index")

# ---- Kreiranje JSON strukture ----
agg_json_list = []

# Grupisanje po godini i facility
grouped = offsite_df.groupby(["Year", "FacilityId"])

for (year, facility_id), group in grouped:
    facility_info = facilities_map.get(facility_id, {})

    # Dodavanje ParentCompany info
    parent_company_id = facility_info.get("ParentCompanyId")
    parent_company_info = companies_map.get(parent_company_id, {}) if parent_company_id else {}

    facility_json = {
        "FacilityId": facility_id,
        "City": facility_info.get("City"),
        "State": facility_info.get("State"),
        "Latitude": facility_info.get("Latitude"),
        "Longitude": facility_info.get("Longitude"),
        "IndustrySector": facility_info.get("IndustrySector"),
        "Federal": True if str(facility_info.get("FederalFacility","NO")).upper() == "YES" else False,
        "ParentCompany": {
            "CompanyId": parent_company_info.get("CompanyId"),
            "CompanyName": parent_company_info.get("CompanyName") or parent_company_info.get("StandardCompanyName")
        }
    }

    all_transfers = []
    offsite_total_all_chemicals = 0.0

    # Grupisanje po hemikaliji unutar facility
    for chemical_id, chem_group in group.groupby("ChemicalId"):
        chem_info = chemicals_map.get(chemical_id, {})
        offsite_release_total_for_chemical = chem_group["OffSiteReleaseTotal"].sum()
        offsite_total_all_chemicals += offsite_release_total_for_chemical

        transfers_for_chemical = chem_group[[
            "POTWTotalTransfers",
            "OffSiteReleaseTotal",
            "OffSiteRecycledTotal",
            "OffSiteEnergyRecoveryTotal",
            "OffSiteTreatedTotal",
            "TotalTransfer",
            "TotalTreatmentIncludingPOTW"
        ]].to_dict(orient="records")

        all_transfers.append({
            "chemical": {
                "ChemicalId": chemical_id,
                "ChemicalName": chem_info.get("ChemicalName"),
                "PFAS": chem_info.get("PFAS", "NO").upper() == "YES",
                "PBT": chem_info.get("PBT", "NO").upper() == "YES",
                "Carcinogen": chem_info.get("Carcinogen", "NO").upper() == "YES",
                "UnitOfMeasure": chem_info.get("UnitOfMeasure"),
                "diseases": json.loads(chem_info.get("Diseases") or "[]"),
                "transfersForChemical": transfers_for_chemical,
                "OffSiteReleaseTotalForChemical": offsite_release_total_for_chemical
            }
        })

    agg_json_list.append({
        "year": int(year),
        "facility": facility_json,
        "allTransfers": all_transfers,
        "OffSiteReleaseTotalForAllChemicals": offsite_total_all_chemicals
    })

# ---- Snimanje JSON fajla ----
with open("OffSiteTransferAggregate.json", "w") as f:
    json.dump(agg_json_list, f, indent=2)

print(f"Generisano {len(agg_json_list)} dokumenta u OffSiteTransferAggregate.json")
