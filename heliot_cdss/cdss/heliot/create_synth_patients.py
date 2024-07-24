import pandas as pd
import uuid
import random
from db_management import DatabaseManagement

# Load the ingredients_synonyms.csv dataset, which contains ingridients and excipients that are in the drug database (tileDB)
ingredients_synonyms = pd.read_csv('ingredients_synonyms.csv', dtype=str, delimiter=';')

# Filter active ingredients and excipients
principi_attivi_distinti = ingredients_synonyms[ingredients_synonyms['type'] == 'active'][['ingredient']]
eccipienti_unici = ingredients_synonyms[ingredients_synonyms['type'] == 'inactive'][['ingredient']]

# Initialize DatabaseManagement
db_manager = DatabaseManagement()
drugs = db_manager.get_all_drugs()

# List to store the synthetic patients 
patients_data = []

# Generate 4975 synthetic patients
for i in range(0, 5):
    
    for drug in drugs:
        drug_code = drug['drug_code']
        ingredients = drug['composition']  # active ingredients
        excipients = drug['excipients']  # excipients
        drug_name = drug['drug_name']
        leaflet = drug['leaflet']
        drug_form_full_descr = drug['drug_form']
        
        if i == 0:
            # Not allergic patient
            status = ""
            allergy = ""
        elif i == 1:
            # Patient allergic to ingredient
            status = 'allergic to ingredient'
            allergy = random.choice(ingredients) if ingredients else ""
        elif i == 2:
            # Patient allergic to excipient
            status = 'allergic to excipient'
            allergy = random.choice(excipients) if excipients else ""
        elif i == 3:
            # Patient not allergic to ingredient
            status = 'not allergic to ingredient'
            allergy = random.choice(principi_attivi_distinti['ingredient'].tolist())
            while allergy in ingredients:
                allergy = random.choice(principi_attivi_distinti['ingredient'].tolist())
        elif i == 4:
            # Patient not allergic to excipient
            status = 'not allergic to excipient'
            allergy = random.choice(eccipienti_unici['ingredient'].tolist())
            while allergy in excipients:
                allergy = random.choice(eccipienti_unici['ingredient'].tolist())
        
        # Generate the patient's UUID 
        patient_id = str(uuid.uuid4())
        
        # Add the new patient 
        patients_data.append({
            "ID": patient_id,
            "drug_name": drug_name,
            "drug_code": drug_code,
            "Allergy": allergy,
            "Status": status,
            "leaflet": leaflet,
            "drug_form_full_descr": drug_form_full_descr
        })

# Create a DataFrame 
patients_df = pd.DataFrame(patients_data)

# Save the dataframe
patients_df.to_excel('patients_synthetic.xlsx', index=False)

print("Dataset 'patients_synthetic.xlsx' successfull created!")
