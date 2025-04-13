import pandas as pd
import numpy as np

# Definizione delle classi di farmaci e loro codici ATC (come prima)
drug_classes = {
    'Opioids': ['N02A'],
    'Antibiotics': ['J01'],
    'NSAID': ['M01A'],
    'Antiplatelet agents': ['B01AC'],
    'Diuretics': ['C03'],
}

# Nuova classificazione degli eccipienti basata sull'articolo
excipient_categories = {
    "Immediate Hypersensitivity Reactions (IHRs)": {
        "Gelatin": ["Gelatina"],
        "Carboxymethylcellulose (CMC)": ["Carbossimetilcellulosa"],
        "PEG and related": [
            "Polietilenglicole",
            "Polisorbati", "polisorbati", "PS20", "PS80", "E433", "E434", "E435", "E436",
            "Poloxameri", "Poloxamer",
            "Cremophor", "olio di ricino poliossietilenato"
        ]
    },
    "Delayed Hypersensitivity Reactions (DHRs)": {
        "Propylene Glycol": ["Glicole propilenico"],
        "Pentylene/Butylene Glycol": [
            "Pentilenglicole", "Glicole polietilenico", "Butilenglicole", 
            "1,3butilenglicole", "butilenglicole", "1,3-Butandiolo", "Butandiolo"
        ]
    },
    "Preservatives": {
        "Parabens": [
            "Parabeni", "parabeni", "Esteri dell'acido p-idrossibenzoico",
            "E218", "E216", "E214", "E209",
            "Metilparabene", "Nipagina", "p-ossibenzoato di metile",
            "Propilparabene", "propilparabene", "p-Idrossibenzoato di propile"
        ],
        "Benzyl Compounds": [
            "Benzalconio cloruro",
            "Alcol benzilico",
            "Benzoato di sodio", "E211",
            "Acido benzoico"
        ]
    },
    "Common Allergens": {
        "Lactose": ["Lattosio"],
        "Egg Proteins": [
            "Proteine dell'uovo", "proteine dell' uovo",
            "Fosfatidi d'uovo purificati", "Ovoalbumina", "Lisozima", "Ovomucina"
        ],
        "Soy Products": ["Prodotti a base di soia", "Soia"],
        "Peanut Oil": ["Olio di arachidi"]
    }
}

def classify_drug(atc_code):
    if pd.isna(atc_code):
        return 'Other'
    
    for class_name, prefixes in drug_classes.items():
        if any(atc_code.startswith(prefix) for prefix in prefixes):
            return class_name
    return 'Other'

def check_excipient(excipient_str, italian_names):
    if pd.isna(excipient_str):
        return False
    excipient_list = excipient_str.split('#')
    return any(any(italian.lower() in exc.lower() for exc in excipient_list) 
              for italian in italian_names)

# Lettura dei dataset
df_drugs = pd.read_excel('drugs_subset.xlsx')
df_excipients = pd.read_excel('drugs_excipients_to_check.xlsx')

# Statistiche dei farmaci
df_drugs['drug_class'] = df_drugs['atc_code'].apply(classify_drug)
drug_stats = df_drugs['drug_class'].value_counts()
print("\nStatistiche per classe di farmaco:")
print(drug_stats)

# Statistiche degli eccipienti per categoria
print("\nStatistiche degli eccipienti per categoria di reazione:")
for category, subcategories in excipient_categories.items():
    print(f"\n{category}:")
    for excipient_name, italian_terms in subcategories.items():
        count = df_excipients['excipient'].apply(
            lambda x: check_excipient(x, italian_terms)
        ).sum()
        if count > 0:
            print(f"  {excipient_name}: {count}")
