# Vodič kroz skup podataka

## Tema
Godišnje prijavljivanje industrijskih hemikalija (TRI, SAD) za **2015–2024**.  
Svaki zapis u bazi je **Godina × Postrojenje × Hemikalija** i obuhvata:  
- **On-site emisije** (vazduh, voda, zemljište, podzemne injekcije).  
- **Off-site transfere** (POTW, odlaganje/ispust, reciklaža, energetski oporavak, tretman).  

## Datoteke
- `2015_us.csv` - `2016_us.csv` - `2017_us.csv` - `2018_us.csv` - `2019_us.csv` - `2020_us.csv` - `2021_us.csv` - `2022_us.csv` - `2023_us.csv` - `2024_us.csv`
 - `basic_data_files_documentation_august_2024.pdf` — zvanična specifikacija polja

**Obim podataka** 
- Zapisa po godini (≈): **75.000** 
-  Ukupno različitih hemikalija: **~600** 
- Savezne države/teritorije: **50** 
- Postrojenja: **25573** 
- Kompanija: **4860**

---

## 📊 Prikupljanje i priprema podataka
Podaci su prikupljeni sa **zvaničnog EPA TRI sajta** putem **web scraping-a**.  
- Za svaku godinu (2015–2024) preuzet je zaseban CSV fajl sa prijavljenim emisijama i transferima.  
- Nakon preuzimanja, svi fajlovi su transformisani i objedinjeni u **jedan veliki integrisani CSV**, čime je obezbeđena konzistentnost i omogućena analiza trenda kroz ceo period.  
- Pored emisija, sa istog izvora dodatno su **skrejpovani i podaci o bolestima** povezanih sa hemikalijama. Na taj način skup je proširen i nadograđen informacijama koje povezuju hemikalije sa zdravstvenim ishodima, čineći ga pogodnijim za interdisciplinarne analize.  

---

## 🏗️ Dizajn šeme i korišćeni šabloni
Rekonstrukcija šeme vođena je principom **aplikacijom vođene šeme** (*Application Driven Schema*), sa ciljem da se struktura optimizuje za najčešće obrasce upita.  

Korišćeni šabloni:  
- **Proširena referenca (Extended Reference)** – izbegnuta su česta spajanja dokumenata tako što su osnovni podaci (npr. ime postrojenja, lokacija, kompanija) uvučeni u referencu. Time je postignuta bolja efikasnost bez prevelike redundanse.  
- **Proračunavanja (Computed Pattern)** – rezultati čestih agregacija (ukupne emisije, zbir transfera) čuvaju se unapred, što značajno ubrzava složene upite i smanjuje opterećenje baze.  

---
## ⚡ Indeksi i optimizacija
U datoteci *indices.txt* definisani su indeksi koji su uvedeni nakon što je analizom upita primećeno gde se javljaju **najčešća filtriranja i pretraživanja**:  

- **Jednostavni indeksi**  
  - `year` — zbog toga što većina upita sadrži vremenske filtere (npr. poređenje emisija kroz godine, analiza trenda). Indeks nad godinom omogućava da se upiti vremenskih serija izvršavaju znatno brže.  
  - `facility.FacilityId` — jer se često filtrira po konkretnom postrojenju (npr. Top 10 postrojenja u državi ili trend za jedno postrojenje).  

- **Složeni indeks**  
  - `year + facility.Latitude + facility.Longitude` — omogućava efikasno grupisanje i poređenja emisija po geografiji, posebno kod upita o koncentraciji emisija u gradovima.  

- **Unikatni indeks**  
  - `DiseaseId` u kolekciji *Diseases* — uveden jer se bolesti često pretražuju unutar niza povezanih sa hemikalijama. Unikatan indeks garantuje jednoznačnost identifikatora bolesti i omogućava brza pretraživanja i spajanja sa hemikalijama.  

Ovi indeksi su direktan odgovor na obrasce upotrebe podataka i ključni su za optimizaciju performansi.  

---



## Osnovne šeme podataka

### 📍 `Reporting Facility` (Postrojenja)
| Kolona | Opis |
|--------|------|
| FacilityId | Jedinstveni identifikator postrojenja |
| FacilityName | Ime postrojenja |
| City, State | Lokacija |
| Latitude, Longitude | Koordinate |
| IndustrySector | EPA industrijski sektor |
| FederalFacility | YES/NO |

---

### 🏢 `Parent Company` (Kompanije)
| Kolona | Opis |
|--------|------|
| CompanyId | Jedinstveni identifikator kompanije |
| CompanyName | Naziv kompanije |
| StandardCompanyName | Standardizovani naziv |

---

### ⚗️ `Chemicals` (Hemikalije)
| Kolona | Opis |
|--------|------|
| ChemicalId | Jedinstveni identifikator hemikalije |
| ChemicalName | Naziv hemikalije |
| UnitOfMeasure |  g |
| PFAS, PBT, Carcinogen | Hazard oznake |
| Diseases | Lista bolesti (JSON niz stringova) |

---

### 🏭 `OnSiteRelease` (On-site emisije)
| Kolona | Opis |
|--------|------|
| Year | Godina |
| FacilityId | Povezano sa `reporting_facility_mongo` |
| ChemicalId | Povezano sa `chemicals_mongo` |
| AirFugitive | Ispusti u vazduh (nekontrolisani) |
| AirStack | Ispusti kroz dimnjake |
| Water | Ispusti u vodu |
| UndergroundInjection | Podzemna injekcija |
| Landfills | Deponije |
| OnSiteReleasesTotal | Zbir svih on-site putanja |

---

### 🚛 `OffSiteTransfer` (Off-site transferi)
| Kolona | Opis |
|--------|------|
| Year | Godina |
| FacilityId | Povezano sa `Reporting Facility` |
| ChemicalId | Povezano sa `Chemicals` |
| POTWTotalTransfers | Javni tretman (POTW) |
| OffSiteReleaseTotal | Odlaganje/ispust van lokacije |
| OffSiteRecycledTotal | Reciklaža |
| OffSiteEnergyRecoveryTotal | Energetski oporavak |
| OffSiteTreatedTotal | Tretman (ne-POTW) |
| TotalTransfer | Ukupni transferi |
| TotalTreatmentIncludingPOTW | Svi tretmani zajedno sa POTW |



## Pregled relacija (ER dijagram)

```mermaid
erDiagram
    COMPANY ||--o{ FACILITY : owns
    FACILITY ||--o{ ONSITE_RELEASE : has
    FACILITY ||--o{ OFFSITE_TRANSFER : has
    CHEMICAL ||--o{ ONSITE_RELEASE : is
    CHEMICAL ||--o{ OFFSITE_TRANSFER : is

    COMPANY {
      string CompanyId PK
      string CompanyName
      string StandardCompanyName
    }

    FACILITY {
      string FacilityId PK
      string FacilityName
      string City
      string State
      float Latitude
      float Longitude
      string IndustrySector
      string FederalFacility "YES/NO"
      string ParentCompanyId
    }

    CHEMICAL {
      string ChemicalId PK
      string ChemicalName
      string UnitOfMeasure
      string PFAS "YES/NO"
      string PBT "YES/NO"
      string Carcinogen "YES/NO"
      json   Diseases
    }

    ONSITE_RELEASE {
      int    Year
      string FacilityId
      string ChemicalId
      float  AirFugitive
      float  AirStack
      float  Water
      float  UndergroundInjection
      float  Landfills
      float  OnSiteReleasesTotal
    }

    OFFSITE_TRANSFER {
      int    Year
      string FacilityId
      string ChemicalId
      float  POTWTotalTransfers
      float  OffSiteReleaseTotal
      float  OffSiteRecycledTotal
      float  OffSiteEnergyRecoveryTotal
      float  OffSiteTreatedTotal
      float  TotalTransfer
      float  TotalTreatmentIncludingPOTW
    }
```


## Upiti

### 1. Top 10 postrojenja u datoj godini i državi 
**Formula:** `OnSiteReleasesTotal + OffSiteReleaseTotal`  
Pronaći najvećih 10 postrojenja sa najvećim ukupnim ispuštanjima u određenoj godini i uz postrojenje prikazati lokaciju, sektor i matičnu kompaniju.

---

### 2. Disposal or Other Releases kroz vreme
Praćenje trenda (2015–2024) koliko je otpada završilo u:  
- Off-site: `OffSiteReleaseTotal`  
- Air: `AirFugitive + AirStack`  
- Water: `Water`  
- Land/Injection: `UndergroundInjection + Landfills`

---

### 3. Waste Management kroz vreme
Analiza toka otpada tokom vremena:  
- Reciklaža: `OffSiteRecycledTotal`  
- Energetski oporavak: `OffSiteEnergyRecoveryTotal`  
- Tretman: `OffSiteTreatedTotal + POTWTotalTransfers`  
- Odlaganje: `OnSiteReleasesTotal + OffSiteReleaseTotal`

---

### 4. Procentualna raspodela po medijumima
Za datu godinu:  
- Air = `(AirFugitive + AirStack) / OnSiteReleasesTotal`  
- Water = `Water / OnSiteReleasesTotal`  
- Land = `(UndergroundInjection + Landfills) / OnSiteReleasesTotal`  

Top 10 hemikalija po `OnSiteReleasesTotal`.

---

### 5. Najčešće bolesti vezane za najviše ispuštane hemikalije (2024)
Za 2024. godinu izdvojiti hemikalije sa najvećim ukupnim ispuštanjima. Iz njihovog polja **Diseases** prebrojati i identifikovati koje se bolesti najčešće povezuju sa ovim hemikalijama.

---

### 6. Top 10 postrojenja po emisiji PBT, Carcinogen ili PFAS hemikalija
Pronaći **10 postrojenja sa najvećim emisijama** koje potiču od hemikalija označenih kao **PBT** , **CANCEROGEN** ili **PFAS**. Rezultat treba da uključi naziv postrojenja, lokaciju (grad, država), industrijski sektor, matičnu kompaniju, kao i ukupnu količinu ispuštenih PBT/PFAS hemikalija izraženu u gramima.

---

### 7. Federal vs Non-Federal postrojenja po industrijskom sektoru
Grupisati po `IndustrySector` i `FederalFacility`.  
Izračunati: ukupno ispuštanja, prosečno po postrojenju, dominantne sektore.

---

### 8. Udeo reciklaže po hemikaliji
Formula:  
`RecycleShare = OffSiteRecycledTotal / (OnSiteReleasesTotal + TotalTreatmentIncludingPOTW)`  

Prikazati Top 10 hemikalija sa najvećim i najmanjim procentom reciklaže.

---

### 9. Promena emisija za odabranu hemikaliju kroz vreme i sektore
Za jednu odabranu hemikaliju (npr. Ammonia) analizirati trend ispuštanja od 2020. do 2024. godine, razbijeno po industrijskim sektorima. Prikazati da li određene industrije smanjuju ili povećavaju emisije te hemikalije, i u kojoj meri.

---

### 10. Geografska koncentracija emisija po gradovima
Za datu godinu sabrati `TotalReleases` po gradu i izračunati:  
- Ukupno ispuštanje  
- Broj postrojenja  
- Prosek po postrojenju  
- Dominantan sektor  

---

## Agregatne šeme (za optimizaciju)

### 🔹 OffSiteTransferAggregate
- Grupisano po **Godina × Facility**.  
- Ugnježdena struktura:  
  - Facility (lokacija, sektor, federal indikator, parent company)  
  - Lista hemikalija (`allTransfers`)  
    - Za svaku hemikaliju: identitet, hazard tagovi, bolesti, sve transfer putanje  

**Primer prostiranja:**
```json
{
  "year": 2015,
  "facility": {
    "FacilityId": "00608DCRBNRD3KM",
    "City": "SALINAS",
    "State": "PR",
    "Latitude": 17.972778,
    "Longitude": -66.231944,
    "IndustrySector": "Chemicals",
    "Federal": false,
    "ParentCompany": {
      "CompanyId": null,
      "CompanyName": null
    }
  },
  "allTransfers": [
    {
      "chemical": {
        "ChemicalId": "0000100425",
        "ChemicalName": "Styrene",
        "PFAS": false,
        "PBT": false,
        "Carcinogen": true,
        "UnitOfMeasure": "Grams",
        "diseases": [
          41,
          42,
          44,
          52
        ],
        "transfersForChemical": [
          {
            "POTWTotalTransfers": 0,
            "OffSiteReleaseTotal": 0,
            "OffSiteRecycledTotal": 0,
            "OffSiteEnergyRecoveryTotal": 0,
            "OffSiteTreatedTotal": 0,
            "TotalTransfer": 0,
            "TotalTreatmentIncludingPOTW": 0
          }
        ],
        "OffSiteReleaseTotalForChemical": 0
      }
    },
    {
      "chemical": {
        "ChemicalId": "N982",
        "ChemicalName": "Zinc compounds",
        "PFAS": false,
        "PBT": false,
        "Carcinogen": false,
        "UnitOfMeasure": "Grams",
        "diseases": [
          41,
          44,
          52
        ],
        "transfersForChemical": [
          {
            "POTWTotalTransfers": 0,
            "OffSiteReleaseTotal": 3243.1854455,
            "OffSiteRecycledTotal": 0,
            "OffSiteEnergyRecoveryTotal": 0,
            "OffSiteTreatedTotal": 0,
            "TotalTransfer": 3243.1854455,
            "TotalTreatmentIncludingPOTW": 0
          }
        ],
        "OffSiteReleaseTotalForChemical": 3243.1854455
      }
    }
  ],
  "OffSiteReleaseTotalForAllChemicals": 3243.1854455
}

```


### 🔹 OnSiteReleaseAggregate
- Grupisano po **Godina × Facility**.  
- Ugnježdena struktura:  
  - Facility (lokacija, sektor, federal indikator, parent company)  
  - Lista hemikalija (`allTransfers`)  
    - Za svaku hemikaliju: identitet, hazard tagovi, bolesti, sve transfer putanje  


**Primer prostiranja:**
```json
{
  "year": 2015,
  "facility": {
    "FacilityId": "27050RJRYN7855A",
    "City": "TOBACCOVILLE",
    "State": "NC",
    "Latitude": 36.233605,
    "Longitude": -80.365201,
    "IndustrySector": "Tobacco",
    "Federal": false,
    "ParentCompany": {
      "CompanyId": "2",
      "CompanyName": "REYNOLDS AMERICAN INC"
    }
  },
  "allReleases": [
    {
      "chemical": {
        "ChemicalId": "0007664417",
        "ChemicalName": "Ammonia",
        "PFAS": false,
        "PBT": false,
        "Carcinogen": false,
        "UnitOfMeasure": "Grams",
        "diseases": [
          37,
          41
        ],
        "releasesForChemical": [
          {
            "Air": 4490110.87063,
            "Water": 0,
            "Underground": 0,
            "Landfills": 0,
            "OnSiteReleaseTotal": 4490110.87063,
            "OnSiteTreatmentTotal": 0
          }
        ],
        "OnSiteReleaseTotalForChemical": 4490110.87063
      }
    },
    {
      "chemical": {
        "ChemicalId": "N503",
        "ChemicalName": "Nicotine and salts",
        "PFAS": false,
        "PBT": false,
        "Carcinogen": false,
        "UnitOfMeasure": "Grams",
        "diseases": [],
        "releasesForChemical": [
          {
            "Air": 6289058.21005,
            "Water": 0,
            "Underground": 0,
            "Landfills": 0,
            "OnSiteReleaseTotal": 6289058.21005,
            "OnSiteTreatmentTotal": 0
          }
        ],
        "OnSiteReleaseTotalForChemical": 6289058.21005
      }
    }
  ],
  "OnSiteReleaseTotalForAllChemicals": 10779169.08068
}
```

## 📈 Poređenje performansi
Pre merenja performansi sprovedena je analiza šeme i indeksa kako bi se obezbedila efikasnost upita:  
- **Normalizacija vs denormalizacija** – izabran kompromis kroz proširene reference.  
- **Preagregacije** – zahvaljujući šablonu proračunavanja, smanjen je broj teških runtime agregacija.  
- **Indeksi** – upiti koji sadrže filtriranje po godini, postrojenju ili bolestima dobijaju višestruko ubrzanje.  

📊 Na grafikonu (*upiti_vremena.png*) prikazano je uporedno vreme izvršavanja pre i posle optimizacije, pri čemu kombinacija šablona i indeksiranja dovodi do značajnog smanjenja latencije.  

![Uporedno vreme izvršavanja upita](upiti_vremena.png)








