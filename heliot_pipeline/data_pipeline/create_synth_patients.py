import pandas as pd
import uuid
import json
import random
from typing import List, Dict

# Random years of reactions
YEARS = ["2000", "2001", "2002", "2003", "2004", "2005",
         "2006", "2007", "2008", "2009", "2010", "2011",
         "2012", "2013", "2014", "2015", "2016", "2017",
         "2018", "2019", "2020", "2021", "2022", "2023",
         "2024", "Jan 2025", "Feb 2025"]

# Random reaction types
LIFE_REACTION_TYPES = ["Anaphylaxis", "Severe Respiratory Depression", "Severe Angioedema", "Severe Bronchospasm", "Severe Cardiovascular Reactions"]
NO_LIFE_IMMUNE_MEDIATED_REACTION_TYPES = ["moderate Nausea hypersensitivity", "moderate Vomiting hypersensitivity", "moderate Diarrhea hypersensitivity", "moderate Hives hypersensitivity", "moderate Itching hypersensitivity", "moderate Rash hypersensitivity", "moderate Swelling hypersensitivity"]
NO_LIFE_NON_IMMUNE_MEDIATED_REACTION_TYPES = ["Nausea side effect, not indicative of hypersensitivity,", "Vomiting side effect, not indicative of hypersensitivity,", "Altered mental status side effect, not indicative of hypersensitivity,", "Itching side effect, not indicative of hypersensitivity,", "Swelling side effect, not indicative of hypersensitivity,", "Costipation side effect, not indicative of hypersensitivity,", "Mild shortness of breath side effect, not indicative of hypersensitivity,"]

# Potential chemical cross-reactivities from literature
POTENTIAL_CHEMICAL_CROSS_REACTIVITY = [{"e":"polyethylene glycol (peg)", "cr":["polysorbates", "poloxamers", "cremophor"]},
                                      {"e":"cremophor", "cr":["polysorbates"]},
                                      {"e":"poloxamers", "cr":["polyethylene glycol (peg)"]},
                                      {"e":"polysorbates", "cr":["cremophor"]},
                                      {"e":"carboxymethylcellulose (cmc)", "cr":["hydroxypropyl methylcellulose (hpmc)", "methylcellulose", "hydroxyethylcellulose"]},
                                      {"e":"propylene glycol", "cr":["pentylene glycol or butylene glycol"]},
                                      {"e":"benzyl alcohol", "cr":["sodium benzoate", "benzoic acid"]},
                                      {"e":"hydroxyethyl starch", "cr":["polysorbates", "poloxamers", "cremophor"]},
                                      {"e":"lanolin", "cr":["propylene glycol", "polyethylene glycol (peg)", "pentylene glycol or butylene glycol"]},
                                      {"e":"hydroxypropyl methylcellulose (hpmc)", "cr":["carboxymethylcellulose (cmc)"]},
                                      {"e":"pentylene glycol or butylene glycol", "cr":["propylene glycol", "polyethylene glycol (peg)"]},
                                      {"e":"methylparaben", "cr":["propylparaben", "parabens"]},
                                      {"e":"hydroxyethylcellulose", "cr":["carboxymethylcellulose (cmc)", "hydroxypropyl methylcellulose (hpmc)", "methylcellulose"]},
                                      {"e":"parabens", "cr":["methylparaben", "propylparaben", "para-aminobenzoic acid (paba)"]}]

# English -> Italian main chemical cross-reactivities
POTENTIAL_CHEMICAL_CROSS_REACTIVITY_IT = {"benzyl alcohol": "alcol benzilico",
                                         "benzoic acid":"acido benzoico",
                                         "cremophor":"cremophor",
                                         "polysorbates":"polisorbati",
                                         "poloxamers": "poloxameri",
                                         "hydroxyethylcellulose": "idrossietilcellulosa",
                                         "methylcellulose": "metilcellulosa",
                                         "sodium benzoate": "benzoato di sodio",
                                         "methylparaben": "metilparabene",
                                         "propylparaben": "propilparabene",
                                         "propylene glycol": "glicole propilenico",
                                         "carboxymethylcellulose (cmc)": "carbossimetilcellulosa",
                                         "pentylene glycol or butylene glycol": "pentilenglicole",
                                         "para-aminobenzoic acid (paba)": "acido para-amminobenzoico",
                                         "hydroxypropyl methylcellulose (hpmc)": "idrossipropilmetilcellulosa",
                                         "polyethylene glycol (peg)":"polietilenglicole" }

# Excipient cross-reactivities to avoid while selecting allergies/intollerances in class "5" 
CROSS_REACTIVITIES_TO_AVOID = [{"e":"benzalkonium chloride", "cr":["parabens","benzoic acid","sodium benzoate", "para-aminobenzoic acid (paba)"]},
                      {"e":"sulfites", "cr":["sodium benzoate", "benzoic acid"]},
                      {"e":"lactose", "cr":["soy-based products", "corn products"]},
                      {"e":"peanut oil", "cr":["soy-based products", "corn products"]},
                      {"e":"propylene glycol", "cr":["polyethylene glycol (peg)", "pentylene glycol or butylene glycol"]},
                      {"e":"benzyl alcohol", "cr":["sodium benzoate", "benzoic acid","methylparaben", "parabens", "para-aminobenzoic acid (paba)"]},
                      {"e":"egg proteins", "cr":["gelatin","soy-based products"]},
                      {"e":"soy-based products", "cr":["peanut oil", "corn products", "egg proteins"]},
                      {"e":"carmine or cochineal", "cr":["tartrazine", "sunset yellow fcf"]},
                      {"e":"tartrazine", "cr":["carmine or cochineal", "sunset yellow fcf", "para-aminobenzoic acid (paba)"]},
                      {"e":"polyethylene glycol (peg)", "cr":["polysorbates", "poloxamers", "cremophor", "propylene glycol", "pentylene glycol or butylene glycol"]},
                      {"e":"poloxamers", "cr":["polysorbates", "polyethylene glycol (peg)", "cremophor", "hydroxyethyl starch"]},
                      {"e":"hydroxyethyl starch", "cr":["polysorbates", "poloxamers", "cremophor"]},
                      {"e":"cremophor", "cr":["polysorbates", "poloxamers", "polyethylene glycol (peg)"]},
                      {"e":"latex", "cr":["soy-based products", "corn products"]},
                      {"e":"carboxymethylcellulose (cmc)", "cr":["hydroxypropyl methylcellulose (hpmc)", "methylcellulose", "hydroxyethylcellulose"]},
                      {"e":"methylcellulose", "cr":["carboxymethylcellulose (cmc)", "hydroxypropyl methylcellulose (hpmc)", "hydroxyethylcellulose"]},
                      {"e":"hydroxyethylcellulose", "cr":["carboxymethylcellulose (cmc)", "hydroxypropyl methylcellulose (hpmc)", "methylcellulose"]},
                      {"e":"pentylene glycol or butylene glycol", "cr":["propylene glycol", "polyethylene glycol (peg)"]},
                      {"e":"sodium benzoate", "cr":["benzoic acid", "methylparaben", "propylparaben", "para-aminobenzoic acid (paba)"]},
                      {"e":"benzoic acid", "cr":["sodium benzoate", "methylparaben", "propylparaben", "para-aminobenzoic acid (paba)", "parabens"]},
                      {"e":"methylparaben", "cr":["para-aminobenzoic acid (paba)", "benzoic acid", "sodium benzoate", "propylparaben", "parabens"]},
                      {"e":"propylparaben", "cr":["methylparaben", "parabens", "benzoic acid", "sodium benzoate", "para-aminobenzoic acid (paba)"]},
                      {"e":"para-aminobenzoic acid (paba)", "cr":["methylparaben", "propylparaben", "parabens", "benzoic acid", "sodium benzoate"]},
                      {"e":"lanolin", "cr":["propylene glycol", "polyethylene glycol (peg)", "pentylene glycol or butylene glycol"]},
                      {"e":"parabens", "cr":["benzyl alcohol", "sodium benzoate", "benzoic acid", "methylparaben", "propylparaben", "para-aminobenzoic acid (paba)"]}
                      ]

# Return the reaction type description
def decode_reaction_type(reaction_type: str) -> str:
    if reaction_type == "None":
        return ""
    elif reaction_type == "Life-threatening":
        r = random.choice(LIFE_REACTION_TYPES)
        return f"{r} reaction"
    elif reaction_type == "Non life-threatening immune-mediated":
        r = random.choice(NO_LIFE_IMMUNE_MEDIATED_REACTION_TYPES)
        return f"{r} reaction"
    elif reaction_type == "Non life-threatening non immune-mediated":
        r = random.choice(NO_LIFE_NON_IMMUNE_MEDIATED_REACTION_TYPES)
        return f"{r}"

# Generate the clinical note for the given case
def generate_clinical_note(case: str, drug_class: str = None, 
                         active_principle: str = None, 
                         excipient: str = None, 
                         reaction_type: str = None,
                         known_allergy: str = None,
                         atc_code: str = None) -> str:
    """Generate a clinical not for a patient case"""
    
    if case.startswith("1"):
        return "No known allergies or intolerances"
    
    year = random.choice(YEARS)
    if case.startswith("2."):
        react = decode_reaction_type(reaction_type)
        return f"Patient showed {react} to {active_principle} ({drug_class}) in {year}"
    
    if case.startswith("3."):
        react = decode_reaction_type(reaction_type)
        return f"Patient showed {react} to {excipient} in {year}"
    
    if case.startswith("4") or case.startswith("5"):
        react = decode_reaction_type(reaction_type)
        return f"Patient patient reports being allergic to {known_allergy} {react} since {year}"
    
    if case.startswith("6."):
        react = decode_reaction_type(reaction_type)
        return f"Patient showed {react} with possible cross-reactivity to {excipient} since {year}"
    
    if case.startswith("7."):
        react = decode_reaction_type(reaction_type)
        return f"Patient showed {react} with possible cross-reactivity within {drug_class} class, specifically to {atc_code} since {year}"
    
    if case.startswith("8"):
        act_ingr_tol = atc_code #random.choice(atc_codes)
        react = decode_reaction_type(reaction_type)
        return f"Patient shows {react} reaction within {drug_class} class but has documented tolerance to {act_ingr_tol} since {year}"
    
    return ""

# Return the act codes for the given drug class
def get_atc_codes_for_class(atc_mapping: List[Dict], drug_class: str) -> List[str]:
    """Ottiene i codici ATC per una specifica drug class"""
    if drug_class != 'Other':
        for class_map in atc_mapping:
            if class_map['class'] == drug_class:
                return [atc['atc'] for atc in class_map['atc_codes']]
    else:
        for class_map in atc_mapping:
            if class_map['class'] in('Non-depolarizing agents', 'ACE Inhibitors', 'TNF inhibitors', 'Antiepileptics', 'Antiarrhythmics', 'Local Anesthetics', 'Antidiabetics'):
                return [atc['atc'] for atc in class_map['atc_codes']]
    return []

# Return the atc descriptions for the given drug class, excluding the atc_to_exclude
def get_atc_codes_names_for_class(atc_mapping: List[Dict], drug_class: str, atc_to_exclude: str) -> List[str]:
    """Ottiene i codici ATC per una specifica drug class"""
    
    if drug_class != 'Other':
        for class_map in atc_mapping:
            if class_map['class'] == drug_class:
                return [atc['name'] for atc in class_map['atc_codes'] if atc['atc'] != atc_to_exclude]
    else:
        for class_map in atc_mapping:
            if class_map['class'] in('Non-depolarizing agents', 'ACE Inhibitors', 'TNF inhibitors', 'Antiepileptics', 'Antiarrhythmics', 'Local Anesthetics', 'Antidiabetics'):
                return [atc['name'] for atc in class_map['atc_codes'] if atc['atc'] != atc_to_exclude]
                    
    return []

# Return the atc descrition, given the atc_code
def get_atc_code_name(atc_mapping: List[Dict], atc_code) -> str:
    for class_map in atc_mapping:
        for atc in class_map['atc_codes']:
            if atc['atc'] == atc_code:
                return atc['name']
    return None

def get_atc_code_name_excluding(atc_mapping: List[Dict], drug_class: str, atc_code_to_exclude:str) -> str:
    al = []
    if drug_class != 'Other':
        for class_map in atc_mapping:
            if class_map['class'] == drug_class:
                for atc in class_map['atc_codes']:
                    if atc['name'] != atc_code_to_exclude:
                        al.append(atc['name'])
    else:
        for class_map in atc_mapping:
            if class_map['class'] in('Non-depolarizing agents', 'ACE Inhibitors', 'TNF inhibitors', 'Antiepileptics', 'Antiarrhythmics', 'Local Anesthetics', 'Antidiabetics'):
                for atc in class_map['atc_codes']:
                    if atc['name'] != atc_code_to_exclude:
                        al.append(atc['name'])        
    if len(al) == 0:
        print(drug_class, atc_code_to_exclude)
    return random.choice(al)

# Return a random active ingredients for all the drug classes, except drug_class_to_exclude
def get_random_active_princ(atc_mapping: List[Dict], drug_class_to_exclude: str) -> str:
    atcs = []
    for class_map in atc_mapping:
        if class_map['class'] == drug_class_to_exclude:
            continue
        else:
            atcs.extend([atc['name'] for atc in class_map['atc_codes']])
    return random.choice(atcs)

# Check cross-reactivity for exciptient_p and excipient_s
def is_to_avoid(excipient_p, excipient_s) -> bool:
    for dictionary in CROSS_REACTIVITIES_TO_AVOID:
        if "e" in dictionary and dictionary["e"] in (excipient_p, excipient_s):
            return True  
    return False

# Return a random excipient (known to be an allergen), excluding excipient_to_exclude
def get_random_excipient(excipients_mapping: List[Dict], excipient_to_exclude:str) -> str:
    excs = []
    print("TO EXCLUDE", excipient_to_exclude)
    for e in excipients_mapping:
        if e['English'].lower() == excipient_to_exclude.lower():
            continue
        else:
            if is_to_avoid(e['English'].lower(), excipient_to_exclude.lower()):
                continue
            excs.append(e['English'].lower())
    print("AT THE END",excs)
    return random.choice(excs)

# Return the classification description for the give case
def decode(case_number:str)->str:
    if case_number.startswith("1"):
        return "NO DOCUMENTED REACTIONS OR INTOLERANCES"
    elif case_number.startswith("2"):
        return "DIRECT ACTIVE INGREDIENT REACTIVITY"
    elif case_number.startswith("3"):
        return "DIRECT EXCIPIENT REACTIVITY"
    elif case_number.startswith("4") or case_number.startswith("5"):
        return "NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS OR EXCIPIENTS"
    elif case_number.startswith("6"):
        return "CHEMICAL-BASED CROSS-REACTIVITY TO EXCIPIENTS"
    elif case_number.startswith("7"):
        return "DRUG CLASS CROSS-REACTIVITY WITHOUT DOCUMENTED TOLERANCE"
    elif case_number.startswith("8"):
        return "DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE"

# Heuristic: check if a potential cross-reactive excipient is in the provided 'excipient' list
def get_potential_cross_reactive_excipients(excipient: str) -> str:
    for e in POTENTIAL_CHEMICAL_CROSS_REACTIVITY:
        if e['e'] in excipient:
            return e["cr"]
    return []

def get_excipients_from_leaflet(drug_name, leaflet_info_df):
    """
    Search for the drug's excipients in the leaflet_info_df DataFrame.
    
    Args:
        drug_name (str): drug name to look for
        leaflet_info_df (pd.DataFrame): DataFrame containing the processed info
    
    Returns:
        str: String containing the drug's excipients, or empty string if no drug found 
    """
    try:
        # Search for the drug in the DataFrame
        result = leaflet_info_df[leaflet_info_df['drug_name'] == drug_name]['excipients']
        
        # IF we found the drug, return the excipients
        if not result.empty:
            return result.iloc[0]
        
        return ""  # Return an empty string if the drug cannot be found 
        
    except Exception as e:
        print(f"Errore nella ricerca degli eccipienti per {drug_name}: {str(e)}")
        return ""

def get_random_excipient_not_cross_reactive() -> str:
    al = ["peanut oil","potassium bisulphite (e228)", "diphenyl (e230)", "orthophenyl phenol sodium", "thiabendazole"]
    return random.choice(al)

# Create the synthetic dataset
def create_prescriptions_dataset(cases: Dict, 
                               drugs_df: pd.DataFrame,
                               leaflet_info_df: pd.DataFrame,
                               excipients_drugs_df: pd.DataFrame,
                               atc_mapping: List[Dict],
                               excipients_mapping: List[Dict]) -> pd.DataFrame:
    """Create the patient synthetic dataset containing prescriptions"""
    
    prescriptions = []
    
    # For each case
    for case in cases['cases']:
        case_number = case['class']
        match_type = case['match_type']
        tolerance = case['tolerance']
        alert = case['alert']
        reaction_types = case['reaction_types']

        # handle drug_class cases
        if 'drug_class_cases' in case:
            for drug_class_case in case['drug_class_cases']:
                drug_class = drug_class_case['drug_class']
                num_cases = drug_class_case['cases']

                # get ATC codes within the drug class 
                atc_codes = get_atc_codes_for_class(atc_mapping, drug_class)
                
                # Filter drugs for the given atc codes within the same drug class
                if atc_codes:
                    relevant_drugs = drugs_df[drugs_df['atc_code'].isin(atc_codes)].copy() # agg
                    if relevant_drugs.empty:
                        relevant_drugs = drugs_df.copy()  # fallback if no match # agg
                else:
                    relevant_drugs = drugs_df.copy()
                
                # If there are not enough drugs, we use all the available drugs with repetitions 
                drugs_sample = relevant_drugs.sample(n=num_cases, replace=True)

                for i in range(num_cases):
                    drug = drugs_sample.iloc[i]
                    known_allergy = None

                    if case_number.startswith("4"): # NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS
                        # we select a random active ingredient (in this case the ATC code) that is not within the drug_class
                        known_allergy = get_random_active_princ(atc_mapping, drug_class)
                    elif case_number.startswith("5"): # NO REACTIVITY TO PRESCRIBED DRUG'S EXCIPIENTS
                        # we select a random excipient that doesn't belong to the list of excipients we use
                        # for all the other cases. It is an heuristic
                        known_allergy = get_random_excipient_not_cross_reactive()
                    
                    # ATC code for the current drug
                    atc_code_name = get_atc_code_name(atc_mapping, drug['atc_code'])

                    if case_number.startswith("7"): # DRUG CLASS CROSS-REACTIVITY WITHOUT TOLERANCE
                        # atc code in the same drug_class but different from the ATC of the current drug
                        atc_code_name = get_atc_code_name_excluding(atc_mapping, drug_class, drug['atc_code'])

                    # Create the prescription
                    prescription = {
                        'patient_id': str(uuid.uuid4()),
                        'drug_code': drug['drug_code'],
                        'drug_name': drug['drug_name'],
                        'clinical_note': generate_clinical_note(
                            case_number,
                            drug_class,
                            drug['active_princ_descr'],  # administered active ingredient 
                            None,  # excipient
                            case['reaction_types'],
                            known_allergy, # active principle different from the one of the prescribed drug
                            atc_code_name # administered atc code
                        ),
                        'classification': case_number,
                        'classification_descr': decode(case_number),
                        'match_type': match_type,
                        'tolerance': tolerance,
                        'alert': alert,
                        'reaction_types': reaction_types,
                        'leaflet': drug['leaflet'],
                        'drug_form_full_descr': drug['drug_form_full_descr'],
                        'prescribed_atc': drug['atc_code']
                    }
                    
                    prescriptions.append(prescription)
        
        # Handle excipient cases 
        elif 'excipient_cases' in case:
            for excipient_case in case['excipient_cases']:
                excipient = excipient_case['excipient']
                num_cases = excipient_case['cases']
                known_allergy = None
                do_print = False

                if case_number.startswith("6."): # CHEMICAL-BASED CROSS-REACTIVITY
                    # get the potential excipients that have know interactions
                    exc_list = get_potential_cross_reactive_excipients(excipient.lower())
                    # Filter drugs that have know chemical cross-reactions.
                    # We start from the excipient case and select potential cross-reactions for the excipient.
                    # Nonetheless, the potential cross-reactive excipients should not be in the drug formulation
                    relevant_drugs = excipients_drugs_df[excipients_drugs_df.apply(lambda row: check_excipient(row['excipient'], get_excipients_from_leaflet(row['drug_name'],leaflet_info_df), exc_list, excipients_mapping, False), axis=1)].copy() # agg
    
                elif case_number.startswith("3."): # EXCIPIENT REACTIVITY
                    # We try to filter excipients that belong to the drug formulation
                    mask = excipients_drugs_df.apply(lambda row: has_any_excipient(row['excipient'], excipient.lower(), excipients_mapping, do_print), axis=1)
                    
                    # Selection of the mask indexes
                    indices = mask[mask].index
                    relevant_drugs = excipients_drugs_df.loc[indices].copy()  
                else:
                    relevant_drugs = excipients_drugs_df.copy()

                # Use the dataset of drugs generated during the drugs_subset creation for the excipient cases
                try:
                    drugs_sample = relevant_drugs.sample(n=num_cases, replace=True)
                except Exception as er:
                    print("Case", case_number, len(relevant_drugs), excipient )
                    raise

                for i in range(num_cases):
                    drug = drugs_sample.iloc[i]
                    
                    prescription = {
                        'patient_id': str(uuid.uuid4()),
                        'drug_code': drug['drug_code'],
                        'drug_name': drug['drug_name'],
                        'clinical_note': generate_clinical_note(
                            case_number,
                            None,  # drug_class
                            None,  # No active principle, we are in excipient cases
                            excipient, # prescribed excipient
                            case['reaction_types'],
                            known_allergy,
                            get_atc_code_name(atc_mapping, drug['atc_code'])
                        ),
                        'classification': case_number,
                        'classification_descr': decode(case_number),
                        'match_type': match_type,
                        'tolerance': tolerance,
                        'alert': alert,
                        'reaction_types': reaction_types,
                        'leaflet': drug['leaflet'],
                        'drug_form_full_descr': drug['drug_form_full_descr'],
                        'prescribed_atc': drug['atc_code']
                    }
                    
                    prescriptions.append(prescription)
            
    return pd.DataFrame(prescriptions)

# 'excipient_string' and 'target_excipients' may contain multiple excipients separated by #
# We check if they have anything in common
def has_any_excipient(excipient_string: str, target_excipients: str, italian_to_english, do_print) -> bool:
    # We split excipient_string. It is in the drugs_excipients_to_check excel file created during the 
    # creation of the drug_subset. 
    excipient_list = excipient_string.lower().split('#')

    # We translate all the excipient from Italian to English
    excipient_list = [italian_to_english.get(term) for term in excipient_list]

    # Check if there is a mach
    result = any(target_excipients in item for item in excipient_list if item is not None)
    
    return result

# Heuristic to find out excipients that have cross reactivities.
# 'excipient_string' and 'formulation' may contain multiple excipients separated by "#".
# They are in Italian. So, we try to translate them in English, due to the fact that
# POTENTIAL_CHEMICAL_CROSS_REACTIVITY_IT contains English terms.
# 'exc_list' contains the potential cross reactive excipients
# 'italian_to_english' is the map that contains the Italian->to->English translations of the excipients
def check_excipient(excipient_string, formulation, exc_list, italian_to_english, do_print):
    # We split excipient_string --> It comes from the drugs_excipients_to_check excel file saved during the 
    # creation of the drug_subset. 
    terms = excipient_string.lower().split('#')
    # We translate them in English
    translated_terms = [italian_to_english.get(term) for term in terms]

    # Check it there is at least 1 term in exc_list, which contains the potential cross reactive excipients
    res = list(set(term for term in translated_terms if term in exc_list))
    
    if do_print and len(res)>0:
        print(f"excipient_string: {excipient_string} formulation:{formulation}", "res", res)

    # We remove the excipients that already are within the drug formulation
    try:
        res = [x for x in res if POTENTIAL_CHEMICAL_CROSS_REACTIVITY_IT.get(x) not in formulation.split("#")]
    except Exception as ee:
        print(res)
        raise 

    return len(res) >0

def main():
    # Load cases 
    with open('patient_cases.json', 'r') as f:
        cases = json.load(f)

    # Load the atc list used to create the drug_subset
    with open('atc.json', 'r') as f:
        atc_mapping = json.load(f)

    # Load the excipient list used to create the drug_subset
    with open('excipients.json', 'r') as f:
        excipients_mapping = json.load(f)

    # Create the Italian->to->English map for the excipients
    italian_to_english = {ita.lower(): item['English'].lower() 
                     for item in excipients_mapping 
                     for ita in item['Italian']}

    # Load the drug_sub set
    drugs_df = pd.read_excel('drugs_subset.xlsx', dtype={'drug_code': str, 'leaflet': str, 'atc_code': str})

    # Load the drugs selected during the creation of the drug subset for the excipients.json 
    excipients_drugs_df = pd.read_excel('drugs_excipients_to_check.xlsx', dtype={'drug_code': str, 'leaflet': str, 'atc_code': str})
    
    # Load the overall info realted to the drug_subset
    leaflet_info_df = pd.read_csv('leaflet_info.csv',)

    # Create the synthetic dataset
    prescriptions_df = create_prescriptions_dataset(cases, drugs_df, leaflet_info_df, excipients_drugs_df, atc_mapping, italian_to_english)
    
    # Save the synthetic dataset
    prescriptions_df.to_excel('patients_synthetic.xlsx', index=False)

if __name__ == "__main__":
    main()
