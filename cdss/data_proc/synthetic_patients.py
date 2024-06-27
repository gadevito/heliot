import pandas as pd
import numpy as np
import re
import uuid

# Loads the drugs dataset
full_drugs = pd.read_excel('drugs.xlsx')
drugs = full_drugs[full_drugs['leaflet'].notna()]

# Loads the excipients dataset
excipients = pd.read_excel('excipients.xlsx', sheet_name='Excipients')

# Loads the ingredients dataset
ingredients = pd.read_excel('ingredients.xlsx')

# Formats the drug's name
def format_drug_name(row):
    full_name = row['drug_name']
    if '*' in full_name:
        # Extracting the drug name before the asterisk
        parts = full_name.split('*')
        drug_name = parts[0].strip()

        # Safe Use of Description and Dosage, Also Managing NaN Values
        drug_form_descr = str(row['drug_form_descr']).strip() if not pd.isna(row['drug_form_descr']) else ""
        drug_dosage = str(parts[1]).strip() if not pd.isna(parts[1]) else ""

        # Creating a list of parts that are not empty
        formatted_parts = [part.upper() for part in [drug_form_descr, drug_dosage] if part]

        # Union of name with description and dosage
        formatted_name = f"{drug_name} {' '.join(formatted_parts)}"

        return formatted_name
    else:
        # If there is no asterisk, return the full name
        return full_name

# generates a unique ID
def generate_unique_id():
    unique_id = uuid.uuid4()
    return str(unique_id)

# Apply the format function 
drugs['formatted_drug_name'] = drugs.apply(format_drug_name, axis=1)

# synthetic dataset generation
np.random.seed(42)
n_patients = 1000

ids = []
for i in range(1, n_patients + 1):
    ids.append(generate_unique_id())

prescriptions = np.random.choice(drugs['formatted_drug_name'], size=n_patients)

# Returns the string in uppercase if it is not None
def safe_uppercase(allergy):
    if pd.isnull(allergy) or allergy == "":
        return None
    return allergy.upper()



#
# Looks for the elements in the given string , 'text', checking if 'text' includes elements.
# Specific means that we want that 'text' contains one of the items in the 'elements' list.
#
def find_element(text, elements, spefific=True, is_ingredient=False):
    if pd.isnull(text) or not isinstance(text, str):
        return None

    text = text.lower().strip()
    matches = set()
    
    # Let's split the text on common separators, removing the surrounding spaces from each component.
    if is_ingredient:
        part_list = [part.strip() for part in re.split(r'[/]', text)]
    else:
        part_list = [part.strip() for part in re.split(r',|;', text)]
    
    for part in part_list:
        for el in elements:
            if part == el.lower():
                matches.add(el)
    
    if spefific:
        # If the ingredient must be contained in the medication
        if matches:
            return safe_uppercase(np.random.choice(list(matches)))
    else:
        # If the ingredient must not be contained in the medication
        non_matches = [el for el in elements if el.lower() not in matches]
        if non_matches:
            return safe_uppercase(np.random.choice(non_matches))

    return None

allergies = []
codes = []
forms = []
leaflets = []
allergy_status = []
current_ingredients = ingredients['Ingredient'].tolist()
current_excipients = excipients['Excipient'].tolist()

# Main loop for the synthetic generation
for index in range(n_patients):
    drug_row = drugs[drugs['formatted_drug_name'] == prescriptions[index]].iloc[0]
    drug_code = str(drug_row['drug_code'])
    codes.append(drug_code.zfill(9))
    forms.append(str(drug_row['drug_form_full_descr']))
    leaflets.append(str(drug_row['leaflet']))
    # 20% of patients are not allergic
    if index < 0.2 * n_patients:
        allergies.append('')
        allergy_status.append('')
    else:
        if index < 0.6 * n_patients: # If the index is between 20% and 60%, the patients have an allergy to an excipient or an active ingredient in the prescribed drug.
            if np.random.rand() < 0.5:
                act_ingr = str(drug_row['active_princ_descr']).strip() if not pd.isna(drug_row['active_princ_descr']) else ""
                #act_ingr = act_ingr.replace("/",";")
                drug = str(drug_row['formatted_drug_name'])

                allergies.append(find_element(act_ingr, current_ingredients, spefific=True, is_ingredient=True))
                allergy_status.append("allergic to ingredient")
            else:
                al = find_element(drug_row['eccipienti'], current_excipients, spefific=True)
                if al is None: # It can happen because, because the column 'eccipienti' has been created starting from leaflets, while the the excipient list comes from the UE and HL7 datasets.
                    
                    act_ingr = str(drug_row['active_princ_descr']).strip() if not pd.isna(drug_row['active_princ_descr']) else ""
                    allergies.append(find_element(act_ingr, current_ingredients, spefific=True, is_ingredient=True))
                    allergy_status.append("allergic to ingredient")                    
                else:
                    allergies.append(al)
                    allergy_status.append('allergic to excipient')
        else: # If the index is between 60% and 100%, the patients have an allergy but it is related to the prescribed drug.
            allergies.append(find_element(drug_row['active_princ_descr'], current_ingredients, spefific=False, is_ingredient=True))
            allergy_status.append("not allergic to ingredient")

# Creates the patients' datasets
patients = pd.DataFrame({
    'ID': ids,
    'Prescription': prescriptions,
    'drug_code': codes,
    'Allergy': allergies,
    'Status': allergy_status,
    'leaflet': leaflets,
    'drug_form_full_descr': forms
})

# Saves the dataset
patients.to_excel('patients_dataset.xlsx', index=False)