from db_management import *
from ingredients_onthology import *
from dss_prompts import *
from leaflets_prompts import *
import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

class GPT4Experiment:
    def __init__(self, db_uri="drugs_db", synonym_csv="ingredients_synonyms.csv"):
        self.dbm = DatabaseManagement(store_lower_case=True)
        self.ont = SynonymManager(synonym_csv)
        # Initialize the OPENAI API
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    # Translate the text in English
    def _translate_in_english(self, text) -> str:
        try:
            response = self.client.chat.completions.create(model="gpt-4o",
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_ENGLISH_TRANSLATION.format(text=text)}],
                                    max_tokens=3000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4: {e}")
            return None

    def _internal_search_drug(self,drug_code:str):
        print("SEARCHING...", drug_code)
        return self.dbm.search_drug(drug_code)

    def dss_check(self, drug_code:str, prescription:str, allergy:str) -> str:
        print("DRUG CODE", drug_code)
        # Use concurrent.futures to process in parallel
        if len(allergy) >0:
            allergy = allergy.lower()
            with ThreadPoolExecutor() as executor:
                future_drug = executor.submit(self._internal_search_drug, drug_code)
                future_translation = executor.submit(self._translate_in_english, allergy)
                    
                # Wait for the results
                drg = future_drug.result()
                allergy = future_translation.result()
                al = self.ont.find_standard_name(allergy)
                allergy_type = "allergic to "+al
        else:
            allergy_type = "not allergic"
            drg = self.dbm.search_drug(drug_code)

        composition = drg['composition']
        excipients = drg['excipients']

        try:
            response = self.client.chat.completions.create(model="gpt-4o",
                                    messages=[{"role": "system", "content": SYSTEM_CHECK_ALLERGY_PROMPT.format(drug=prescription, active_ingredients=composition, excipients=excipients)},
                                            {"role": "user", "content":  USER_CHECK_ALLERGY_PROMPT.format( allergy=allergy_type)}],
                                    max_tokens=3000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4: {e}")
            return None

'''
def main():
    experiment = GPT4Experiment()
    patients_df = pd.read_excel('patients_complete.xlsx', dtype=str)
    # Sostituisci i valori NaN con stringhe vuote
    patients_df.fillna('', inplace=True)

    patients_df['drug_code'] = patients_df['drug_code'].astype(str)
    patients_df['drug_name'] = patients_df['drug_name'].astype(str)
    patients_df['Status'] = patients_df['Status'].astype(str)
    patients_df['Allergy'] = patients_df['Allergy'].astype(str)
    patients_df['ID'] = patients_df['ID'].astype(str)

    results = []

    print("DATASETS OPENED")
    count = 1
    nrows = patients_df.shape[0]
    # Checks each patient
    for _, row in patients_df.iterrows():
        drug_code = str(row['drug_code'])
        prescription = str(row['drug_name'])
        status = str(row['Status'])
        allergy = str(row['Allergy']).strip() if not pd.isna(row['Allergy']) else ""
        patient_id = str(row['ID'])
        print("INFO", drug_code, prescription, allergy, status)
        result = experiment.dss_check(drug_code, prescription, allergy)
        if not len(allergy)>0:
            status ="Not allergic"
        results.append({'ID': patient_id, 'Result': result, 'Status': status})
        print(count, "/", nrows)
        count +=1

    # Creates the results dataframe and saves it
    results_df = pd.DataFrame(results)
    results_df.to_excel('results.xlsx', index=False)
'''

def process_row(experiment, row):
    drug_code = str(row['drug_code'])
    prescription = str(row['drug_name'])
    status = str(row['Status'])
    allergy = str(row['Allergy']).strip() if not pd.isna(row['Allergy']) else ""
    patient_id = str(row['ID'])
    result = experiment.dss_check(drug_code, prescription, allergy)
    if not len(allergy) > 0:
        status = "Not allergic"
    return {'ID': patient_id, 'Result': result, 'Status': status}

def main():
    experiment = GPT4Experiment()
    patients_df = pd.read_excel('patients_complete.xlsx', dtype=str)
    # Update NaN with empty strings
    patients_df.fillna('', inplace=True)

    patients_df['drug_code'] = patients_df['drug_code'].astype(str)
    patients_df['drug_name'] = patients_df['drug_name'].astype(str)
    patients_df['Status'] = patients_df['Status'].astype(str)
    patients_df['Allergy'] = patients_df['Allergy'].astype(str)
    patients_df['ID'] = patients_df['ID'].astype(str)

    print("DATASETS OPENED")

    results = []
    nrows = patients_df.shape[0]

    # Using ThreadPoolExecutor the parallel execute the assessment
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_row = {executor.submit(process_row, experiment, row): row for _, row in patients_df.iterrows()}
        
        count = 1
        for future in as_completed(future_to_row):
            try:
                result = future.result()
                results.append(result)
                print(count, "/", nrows)
                count += 1
            except Exception as e:
                print(f"Row processing generated an exception: {e}")

    # Create the DataFrame with the risults and save it to and Excel file.
    results_df = pd.DataFrame(results)
    results_df.to_excel('results.xlsx', index=False)

if __name__ == "__main__":
    main()