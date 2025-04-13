import pandas as pd
import json
import argparse
from tqdm import tqdm

    
def process_atc(df_filtered):
    result_df = pd.DataFrame()
    data = []
    with open('atc.json', 'r') as file:
        data = json.load(file)

    atc_codes = {}
    for classes in data:
        for c in classes['atc_codes']:
            atc_codes[c['atc']] = c['qty']

    print("=====> PROCESSING ATC CODES")
    # Now we have the dictionary for atc codes, let's randomly select drugs belonging to the atc codes
    
    for atc in tqdm(atc_codes, desc="Generating samples for atc codes"):
        df_atc = df_filtered[df_filtered['atc_code'] == atc]
        samples = atc_codes[atc]
        dim = df_atc.shape[0]
        if dim < samples:
            print(f"ATC CODE WITH LESS DATA {atc}")
        samples = min(samples, dim)
        # Let's make it reproducible and let's randomly select 'samples' drugs
        random_drug_codes = df_atc['drug_code'].sample(n=samples, random_state=42)

        # Extract all columns for the selected drug codes
        df_random = df_filtered[df_filtered['drug_code'].isin(random_drug_codes)]
        result_df = pd.concat([result_df, df_random], ignore_index=True)

    print(f"GENERATED {result_df.shape[0]} DRUGS FOR ATC")
    return result_df

def ignore_condition(term, content, drug_code):
    if term == "lanolina" and "lanolina anidra" in content:
        return True
    if term == "lanolina" and "lanolina idrogenata" in content:
        return True
    if term == "benzoato di sodio" and "Metil-paraidrossibenzoato di sodio" in content:
        return True
    if term == "benzalconio cloruro" and drug_code in("017076148", "038197012"):
        return True
    if term == "alcol benzilico" and drug_code in ("024352179", "024352066", "024352229"):
        return True
    if term == "carmine" and ("indigo carmine" in content) or ("lacca indigotina carmine alluminio") in content:
        return True
    if term == "lattice" and "non contengono lattice" in content:
        return True
    if term == "lattosio" and "lattosio monoidrato" in content:
        return True
    if term == "lisozima" and "lisozima cloridrato" in content:
        return True
    return False

def process_excipients(df_all_drugs, df_drugs):
    result_df = pd.DataFrame()
    excipients_df = pd.DataFrame()
    # First of all, let's open leafleats to check if they contain the excipients comprised in excipients.json
    # We store leafleats and drugs for subsequent processing
    data = []
    with open('excipients.json', 'r') as file:
        data = json.load(file)

    excluded_drug_codes = df_drugs['drug_code'].tolist()

    # filtered_df contains only non-processed drug codes (see process_atc)
    filtered_df = df_all_drugs[~df_all_drugs['drug_code'].isin(excluded_drug_codes)]

    potential_drugs = set()
    drugs_dict = {}
    
    print("SEARCHING FOR LEAFLETS CONTAINING EXCIPIENTS.....")
    
    # Pre-compile all th strings to search 
    all_terms = {}
    for e in data:
        for name in e['Italian']:
            all_terms[name.lower()] = e
    all_terms = list(all_terms.items())  # convert to ituple list (name, excipient)
    
    for term, excipient in all_terms:
        print(term+" "+str(excipient))

    # Sections for excipients in leaflets 
    COMP_SECTION = '<h2><a name="Titolo_02">02.0 COMPOSIZIONE QUALITATIVA E QUANTITATIVA'.lower()
    PHARM_FORM = '<h2><a name="Titolo_17">03.0 FORMA FARMACEUTICA</a>'.lower()
    EXCIPIENT_SECTION = '<h3><a name="SottoTitolo_03">06.1 Eccipienti'.lower()
    INCOMP_SECTION = '<h3><a name="SottoTitolo_11B">06.2 Incompatibilita'.lower()

    # Iterate over leaflets 
    for index, row in tqdm(filtered_df.iterrows(), desc='Searching in leaflet files'):
        drug_code = row['drug_code']
        if drug_code in potential_drugs:
            continue
        
        try:
            with open(f"./documents/{row['leaflet']}", 'rb') as file:
                content = file.read().decode('latin-1', errors='ignore').lower()
                i= content.find(COMP_SECTION)
                j= content.find(PHARM_FORM)
                k= content.find(EXCIPIENT_SECTION)
                l= content.find(INCOMP_SECTION)
                content = content[i:j]+"\n"+content[k:l]

                # Search for all the excipients 
                for term, excipient in all_terms:
                    if ignore_condition(term, content, drug_code):
                        continue
                    if term in content:
                        potential_drugs.add(drug_code)
                        drugs_dict[drug_code] = excipient
                        break
                        
        except Exception as e:
            print(f"Error while reading file {row['leaflet']}: {str(e)}")
            continue
        
    excipients = {}
    # Here potential_drugs contains drugs that potentially have the need excipients
    # So, let's iterate over potential_drugs and let's add the necessary samples to the drugs_subset data frame
    print(f"GENERATE SAMPLES FOR EXCIPIENTS {len(potential_drugs)}.....")
    for drug_code in tqdm(potential_drugs, 'Generating samples for excipients'):
        row = filtered_df.loc[filtered_df['drug_code'] == drug_code].iloc[0]
        # Now we can get the excipient and add the number of necessary samples
        excipient = drugs_dict[drug_code]
        excipient_name = excipient['English']
        if excipient_name in excipients:
            excipient = excipients[excipient_name]
        else:
            excipients[excipient_name] = excipient

        if excipient['qty'] >0:
            result_df = pd.concat([result_df, row.to_frame().T], ignore_index=True)
            drug_row = row.to_frame().T
            excipient_row = drug_row.copy()
            excipient_row['excipient'] = "#".join(excipient['Italian'])  # Aggiungi il nome dell'eccipiente in italiano
            excipients_df = pd.concat([excipients_df, excipient_row], ignore_index=True)
            excipient['qty'] = excipient['qty']-1

    print(f"GENERATED {result_df.shape[0]} DRUGS FOR EXCIPIENTS")
    # Print not found excipients
    for e in data:
            if e['English'] in excipients:
                rx = excipients[e['English']]
                if rx['qty'] > 0:
                    print(rx['English'])
            else:
                print(e['English'], "NOT FOUND")

    excipients_df.to_excel("drugs_excipients_to_check.xlsx", index=False)
    result_df = pd.concat([result_df, df_drugs], ignore_index=True)
    return result_df

def main(output_file):
    # Read the drugs dataset
    df = pd.read_excel('drugs.xlsx', dtype={'drug_code': str, 'leaflet': str, 'atc_code': str})
    # Filtering rows where 'leaflet' is not empy
    df_filtered = df.dropna(subset=['leaflet'])

    df_drugs = process_atc(df_filtered)
    df_drugs = process_excipients(df_filtered, df_drugs)

    print(f"WRITING {df_drugs.shape[0]} DRUGS TO THE DRUGS_SUBSET")
    # Let's write the drugs_subset.xlsx file
    df_drugs.to_excel(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract drugs accordingly to atc codes and excipients as defined in the respective json files.")
    parser.add_argument('-o', '--output_file', 
                    type=str, 
                    default='drugs_subset.xlsx',
                    help='Excel file name to write. Default: drugs_subset.xlsx')

    args = parser.parse_args()

    main(args.output_file)