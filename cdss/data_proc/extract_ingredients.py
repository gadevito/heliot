import pandas as pd

# Carica il dataset da un file Excel
df = pd.read_excel('dataset.xlsx', dtype={'drug_code': "string",
                                          "countable" :"string",
                                          "solvent" : "string",
                                          "senza_fustella" : "string",
                                          "drug_name" : "string",
                                          "drug_dosage" : "string",
                                          "drug_form_code" : "string",
                                          "drug_form_descr" : "string",
                                          "drug_form_full_descr" : "string",
                                          "abstract_drug_code" : "string",
                                          "abstract_drug": "string",
                                          "num_units": "string",
                                          "commercial_state": "string",
                                          "cod_tipo_prodotto": "string",
                                          "desc_tipo_prodotto": "string",
                                          "active_princ_code": "string",
                                          "active_princ_descr": "string",
                                          "atc_code": "string",
                                          "leaflet": "string"})

# Estrai la colonna dei principi attivi
active_principles = df['active_princ_descr']

# Separa i principi attivi dove ci sono "/" e raccoglie tutto in una lista
principi_attivi_distinti = set()
for entry in active_principles.dropna():
    split_principles = entry.split('/')
    for principle in split_principles:
        principi_attivi_distinti.add(principle.strip())

# Converti il set in DataFrame per esportarlo
principi_attivi_df = pd.DataFrame(principi_attivi_distinti, columns=['Ingredient'])

# Salva il DataFrame in un nuovo file Excel
principi_attivi_df.to_excel('ingredients.xlsx', index=False)

print('File Excel con i principi attivi distinti è stato creato.')