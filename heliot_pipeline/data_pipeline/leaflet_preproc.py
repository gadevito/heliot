from typing import List
from leaflet_info_extractor import LeafletInfo, LeafletInfoExtractor
import pandas as pd
import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import copy
from leaflets_prompts import *
import urllib.parse
import json
import traceback
from tqdm import tqdm


# Initialize the OPENAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class MalformedURLException(Exception):
    """Personalized Exception to handle malformed URLs."""
    pass

# Leaflet Data Preprocessing 
class LeafletInfoPreProcessor:
    def __init__(self, model ="gpt-4o", dataset_name="drugs_subset.xlsx", path="./documents", dictionary_name="ingredients_synonyms.csv"):
        self.model = model
        #Load the dataset
        self.dataset_name = dataset_name
        #self.df = pd.read_excel(dataset_name,dtype=str)
        #self.df['drug_code'] = self.df['drug_code'].astype(str)
        self.ingredients = {}
        self.dictionary_name= dictionary_name
        self.lp = LeafletInfoExtractor(path)
        self.cache = {}
        self.drug_cache = {}
        self.retries = 3

    # Update the dictionary if the key doesn't exist
    def update_dictionary(self, composition, excipients):
        lc = composition.split("#")
        le = excipients.split("#")
        for lr in lc:
            l = lr.lower().strip()
            if l in self.ingredients:
                continue
            self.ingredients[l] = {"type":"active", "synonyms":[]}

        for lr in le:
            l = lr.lower().strip()
            if l in self.ingredients:
                continue
            self.ingredients[l] = {"type":"inactive", "synonyms":[]}

    # Save the ingredients dictionary baseline, without the synonyms
    def save_dictionary(self):
        cont = 0
        print("INGREDIENTS FOUND", len(self.ingredients))

        # Wrapping function to maintain the ingredient's original name and its translation
        def translate_ingredient(k):
            return k, self._translate_in_english(k)

        # Use ThreadPoolExecutor to parallelize translations
        num_threads = os.cpu_count() * 4 #era 2
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_ingredient = {executor.submit(translate_ingredient, k): k for k in self.ingredients}

            for future in as_completed(future_to_ingredient):
                k, ek = future.result()
                if ek.find("no inactive ingredients") != -1 or ek.find("no active ingredients") !=-1:
                    continue
                self.ingredients[k]['english_name'] = ek
                cont += 1
                if cont % 100 == 0:
                    print("TRANSLATED", cont)

        data = []
        for ingredient, info in self.ingredients.items():
            data.append({
                'ingredient': ingredient,
                'english_name': info.get('english_name', ''),
                'type': info['type'],
                'synonyms': '#'.join(info.get('synonyms', []))
            })

        new_df = pd.DataFrame(data)
        dictionary_cols = ['ingredient', 'english_name', 'type', 'synonyms', 'processed']
        
        if os.path.exists(self.dictionary_name):
            # If the CSV exists, read it
            existing_df = pd.read_csv(self.dictionary_name, encoding='utf-8', dtype=str)
            
            # Check if new_df has the same columns of existing_df
            for col in existing_df.columns:
                if col not in new_df.columns:
                    new_df[col] = ''  # Add the missing column

            # Search for all the ingredients that are not in the CSV
            new_df = new_df[~new_df['ingredient'].isin(existing_df['ingredient'])]
            
            # Add the new ingredients to the existing dataframe
            combined_df = pd.concat([existing_df, new_df], ignore_index=True, sort=False)
            
            # Write the combined DataFrame to the CSV
            combined_df.to_csv(self.dictionary_name, index=False, encoding='utf-8')
        else:
            # Check if new_df has all the needed columns, adding the missing ones
            for col in dictionary_cols:
                if col not in new_df.columns:
                    new_df[col] = ''
            
            # If the CSV doesn't exist, we create it
            new_df.to_csv(self.dictionary_name, index=False, encoding='utf-8')


    # Process the synonyms for the ingredients
    def process_synonyms(self):
        while True:
            try:
                # Read the dictionary dataset
                try:
                    df = pd.read_csv(self.dictionary_name, dtype=str)
                except Exception:
                    df = pd.read_csv(self.dictionary_name,delimiter=';', dtype=str)

                df['english_name'] = df['english_name'].astype(str)
                df['synonyms'] = df['synonyms'].astype(str)

                # Add the "processed" column if it doesn't exist
                if 'processed' not in df.columns:
                    df['processed'] = 'NO'

                # Set any empty processed values to 'NO'
                df['processed'] = df['processed'].fillna('NO')

                # Add the "synonyms" column if it doesn't exist
                if 'synonyms' not in df.columns:
                    df['synonyms'] = ""

                # Process all the ingredients
                for index, row in df.iterrows():
                    if row['processed'] == 'NO':
                        try:
                            ek = row['english_name'].replace("/","-")
                            print(ek)
                            synonyms = self._get_pubchem_synonyms(ek)

                            print("synonyms for", ek, synonyms)
                            # Concat synonynms into a single string where synonyms are separated by "#"
                            if synonyms:
                                synonyms_str = "#".join(synonyms)
                            else:
                                synonyms_str = ""
                            df.at[index, 'synonyms'] = synonyms_str
                            
                            # if there are no errore, we set processes to yes
                            df.at[index, 'processed'] = 'YES'
                        except Exception as e:
                            # If there is an exception, we set processed to "no", so we can retry later
                            df.at[index, 'processed'] = 'NO'
                            df.to_csv(self.dictionary_name, index=False)
                            raise e
                    if index % 50 == 0:
                        print("SYNONYMS",index)
                # Save the updated dataset 
                df.to_csv(self.dictionary_name, index=False)
                return True
            except Exception as e:
                print(f"Error during the synonyms processing: {e}")
                # Optionally, it saves the current dataset
                if 'df' in locals():
                    df.to_csv(self.dictionary_name, index=False)
                    if isinstance(e,MalformedURLException):
                        # Here we have a Malformed-url problem, maybe the english translation contains illegal characters. 
                        # We must check it manually
                        return False
                    time.sleep(5)
                    continue
                else:
                    raise


    # Populate the synonyms for the dictionary elements and write the result as a csv file
    def populate_synonyms(self):
        print("TOTAL elements", len(self.ingredients))
        
        cont = 0
        for k in self.ingredients:
            # k is the standard name in lower case
            ek =self._translate_in_english(k)
            synonyms = self._get_pubchem_synonyms(ek)
            if synonyms:
                self.ingredients[k]["synonyms"] = synonyms
            cont +=1
            if cont % 50 == 0:
                print(cont)
            time.sleep(1)  # We pause the current thread for 1 second
            
        # Create a DataFrame using the dictionary
        data = []
        for ingredient, info in self.ingredients.items():
            data.append({
                'ingredient': ingredient,
                'type': info['type'],
                'synonyms': '#'.join(info.get('synonyms', []))
            })

        df = pd.DataFrame(data)
        
        # Export DataFrame as CSV
        df.to_csv(self.dictionary_name, index=False, encoding='utf-8')

    # Uses Pubchem to get the synonyms of the ingredient_name
    def _get_pubchem_synonyms(self, ingredient_name):
        session = requests.Session()  # Uso di una sessione persistente

        def fetch_synonyms(url):
            try:
                response = session.get(url, timeout=40)  # Timeout 10 seconds
                if response.status_code == 404:
                    print(f"No synonyms found (404) for URL: {url}")
                    return []
                response.raise_for_status()  # Genera un'eccezione se status_code != 200
                data = response.json()
                try:
                    synonyms = data['InformationList']['Information'][0]['Synonym']
                    return [synonym.lower() for synonym in synonyms]
                except (KeyError, IndexError):
                    print(f"No synonyms found in the response from URL: {url}")
                    return []
            except requests.exceptions.RequestException as e:
                if "Bad Request" in str(e):
                    raise MalformedURLException(f"Malformed URL encountered: {url}")
                print(f"Request exception: {e}")
                raise  # Lanciare l'eccezione per la gestione nella funzione chiamante

        # Encode ingredient_name to handle special characters
        encoded_ingredient_name = urllib.parse.quote(ingredient_name)

        url_compound = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded_ingredient_name}/synonyms/JSON"
        synonyms = fetch_synonyms(url_compound)

        if not synonyms:
            url_substance = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{encoded_ingredient_name}/synonyms/JSON"
            synonyms = fetch_synonyms(url_substance)

        return synonyms

    def _process_single_leaflet(self, drug_code, drug_name, atc, leaflet, drug_form_full_descr="", excipients="", composition="", parallel=True) -> LeafletInfo:
        # If the leaflet is empty, it means that the drug has been retracted, and we cannot process it
        if pd.isna(leaflet):
            leaflet_info = LeafletInfo()
            leaflet_info.drug_code = drug_code
            leaflet_info.drug_name = drug_name
            leaflet_info.leaflet = leaflet
            leaflet_info.atc = atc
            leaflet_info.drug_form = drug_form_full_descr
        else:
            if drug_code in self.drug_cache:
                leaflet_info = self.drug_cache[drug_code]
            else:
                # Given that a leaflet is valid for more than one pharmaceutical form, we use a cache
                if leaflet in self.cache:
                    leaflet_info_o = self.cache[leaflet]
                    leaflet_info = copy.deepcopy(leaflet_info_o)
                    leaflet_info.drug_code = drug_code
                    leaflet_info.drug_name = drug_name
                    leaflet_info.drug_form = drug_form_full_descr
                    leaflet_info.atc = atc
                else:
                    leaflet_info = self.lp.loadLeafletFile(drug_code, drug_name, drug_form_full_descr,leaflet)
                    leaflet_info.atc = atc
                    self.cache[leaflet] = copy.deepcopy(leaflet_info)
                
                self.drug_cache[drug_code] = leaflet_info

            # Proprocess the leaflet data using GPT-4

            if parallel:
                # Use concurrent.futures to process in parallel
                with ThreadPoolExecutor() as executor:
                    future_composition = executor.submit(self._process_active_ingredients, drug_name, drug_form_full_descr, leaflet_info.composition)
                    future_excipients = executor.submit(self._process_excipients, drug_name, drug_form_full_descr, leaflet_info.PharmaInfo.get("excipients", ""))
                    future_posology = executor.submit(self._process_posology, drug_name, drug_form_full_descr, leaflet_info.clinicalInfo.get("posology", ""))
                    
                    # Wait for the results
                    leaflet_info.composition = future_composition.result()
                    leaflet_info.PharmaInfo["excipients"] = future_excipients.result()
                    leaflet_info.clinicalInfo["posology"] = future_posology.result()
            else:
                leaflet_info.composition = self._process_active_ingredients(drug_name, drug_form_full_descr, leaflet_info.composition)
                leaflet_info.PharmaInfo["excipients"] = self._process_excipients(drug_name, drug_form_full_descr, leaflet_info.PharmaInfo.get("excipients", ""))
                leaflet_info.clinicalInfo["posology"] = self._process_posology(drug_name, drug_form_full_descr, leaflet_info.clinicalInfo.get("posology", ""))
            
            #leaflet_info.composition = self._process_active_ingredients(drug_name, drug_form_full_descr, leaflet_info.composition)
            #leaflet_info.PharmaInfo["excipients"] = self._process_excipients(drug_name, drug_form_full_descr,leaflet_info.PharmaInfo["excipients"])
            #leaflet_info.clinicalInfo["special_warnings"] = self._process_special_warnings(drug_name, drug_form_full_descr, leaflet_info.clinicalInfo["special_warnings"])
            #leaflet_info.clinicalInfo["posology"] = self._process_posology(drug_name, drug_form_full_descr, leaflet_info.clinicalInfo["posology"])
            #leaflet_info.clinicalInfo["contraindications"] = self._process_contraindications(drug_name, drug_form_full_descr, leaflet_info.clinicalInfo["contraindications"])
            #leaflet_info.clinicalInfo["drug_interactions"] = self._process_drug_interactions(drug_name, drug_form_full_descr, leaflet_info.clinicalInfo["drug_interactions"])
            #leaflet_info.PharmaInfo["incompatibilities"] = self._process_drug_incompatibilities(drug_name, drug_form_full_descr, leaflet_info.PharmaInfo["incompatibilities"])

            #leaflet_info.composition = composition.replace("/","#")
            #leaflet_info.PharmaInfo["excipients"] = excipients.replace(",","#").replace("/","#")
            self.update_dictionary(leaflet_info.composition, leaflet_info.PharmaInfo["excipients"])
            leaflet_info.cross_reaction = self._process_cross_reactions(drug_name, leaflet_info.composition, leaflet_info.clinicalInfo["special_warnings"])

            '''
                cont += self.lp.num_tokens_from_string(leaflet_info.composition)
                cont += self.lp.num_tokens_from_string(leaflet_info.PharmaInfo["excipients"])
                cont += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["special_warnings"])
                cont += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["posology"])
                cont += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["contraindications"])
                cont += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["drug_interactions"])
                cont += self.lp.num_tokens_from_string(leaflet_info.PharmaInfo["incompatibilities"])
                
                leaflet_info.excipients_tokens += self.lp.num_tokens_from_string(leaflet_info.PharmaInfo["excipients"])
                leaflet_info.special_warnings_tokens += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["special_warnings"])
                leaflet_info.posology_tokens += self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["posology"])
                leaflet_info.contraindications_tokens = self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["contraindications"])
                leaflet_info.drug_interactions_tokens = self.lp.num_tokens_from_string(leaflet_info.clinicalInfo["drug_interactions"])
                leaflet_info.incompatibilities_tokens = self.lp.num_tokens_from_string(leaflet_info.PharmaInfo["incompatibilities"])
            '''
        return leaflet_info

    # process a single row, creating the leaflet info
    def process_row(self, index, row):
        drug_name = row['drug_name']
        drug_code = row['drug_code']
        leaflet = row['leaflet']
        atc = row['atc_code']

        try:
            excipients = str(row['eccipienti'])
            composition = row['active_princ_descr']
        except:
            excipients = None
            composition = None
        drug_form_full_descr = row['drug_form_full_descr']
        # If it has already been processed, we simply ignore it
        if row['preprocessed'] == "OK":
            print("ALREADY PROCESSED", drug_code)
            return None

        try:
            result = self._process_single_leaflet(drug_code, drug_name, atc, leaflet, drug_form_full_descr, excipients, composition)
        except Exception as ee:
            result = self._process_single_leaflet(drug_code, drug_name, atc, leaflet, drug_form_full_descr, excipients, composition, False)
        #if index % 100 == 0:
        #    print("INDEX ", index)

        if result is None:
            print("RESULT IS NONE", drug_code)
        return result

    # Use Multithreading to process drugs
    def parallel_process_leaflets(self) -> List[LeafletInfo]:
        results = []
        self.df = pd.read_excel(self.dataset_name,dtype={'drug_code': str, 'leaflet': str, 'atc_code': str})
        self.df['drug_code'] = self.df['drug_code'].astype(str)
        # Add the new column if it doesn't exist
        if 'preprocessed' not in self.df.columns:
            self.df['preprocessed'] = "NO"
        else:
            self.df['preprocessed'] = self.df['preprocessed'].astype(str)

        # Get the number of drugs in the dataset
        nrows = self.df.shape[0]

        # Stampa il numero di righe
        print(f"Number of Drugs: {nrows}")

        cont = 0
        num_threads = os.cpu_count() * 2 #era 4
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(self.process_row, index, row): index for index, row in self.df.iterrows()}
            #for future in as_completed(futures):
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                if result is not None:
                    results.append(result)
                else:
                    print("Result None",future, future.cancelled, future.exception)
                cont += 1
                if cont % 30 == 0 and self.model == "gpt-4o":
                    time.sleep(10)

        print("TOTAL ROWS", cont, len(results))

        return results

    # Process the leaflets sequentially
    def process_leaflets(self) -> List[LeafletInfo]:
        results = []
        self.df = pd.read_excel(self.dataset_name,dtype=str)
        self.df['drug_code'] = self.df['drug_code'].astype(str)
        # Add the new column if it doesn't exist
        if 'preprocessed' not in self.df.columns:
            self.df['preprocessed'] = "NO"
        else:
            self.df['preprocessed'] = self.df['preprocessed'].astype(str)
        # For each drug in the dataset
        for index, row in self.df.iterrows():
            r = self.process_row(index, row)
            if r is None:
                continue

            results.append(r)
        return results

    # Translate the text in English
    def _translate_in_english(self, text) -> str:
        try:
            response = client.chat.completions.create(model=self.model,
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_ENGLISH_TRANSLATION.format(text=text)}],
                                    max_tokens=3000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4 _translate_in_english: {e}")
            return None


    def _process_active_ingredients(self, drug_name, form,  composition) -> str:
        '''Use GPT-4 to process the composition'''
        backoff_factor=1.0
        for attempt in range(self.retries):
            try:
                response = client.chat.completions.create(model=self.model,
                                        messages=[{"role": "system", "content": ""},
                                                {"role": "user", "content":  USER_PROCESS_ACTIVE_INGREDIENTS.format(drug_name=drug_name, drug_form=form, composition=composition)}],
                                        max_tokens=1000,
                                        temperature = 0)
                cleaned_text = response.choices[0].message.content
                return cleaned_text
            except Exception as e:
                print(f"Failed to process text with GPT-4 _process_active_ingredients: {e}")
                wait = backoff_factor * (2 ** attempt)
                time.sleep(wait)
        raise Exception(f"Max retries exceeded {self.model}")

    def _process_excipients(self, drug_name, form,  composition) -> str:
        '''Use GPT-4 to process the inactive ingredients'''
        backoff_factor=1.0
        for attempt in range(self.retries):
            try:
                response = client.chat.completions.create(model=self.model,
                                        messages=[{"role": "system", "content": ""},
                                                {"role": "user", "content":  USER_PROCESS_INACTIVE_INGREDIENTS.format(drug_name=drug_name, drug_form=form, composition=composition)}],
                                        max_tokens=4000,
                                        temperature = 0)
                cleaned_text = response.choices[0].message.content
                if cleaned_text.startswith("<<ALL>>"):
                    return composition
                
                return cleaned_text
            except Exception as e:
                print(f"Failed to process text with GPT-4 _process_excipients: {e}")
                wait = backoff_factor * (2 ** attempt)
                time.sleep(wait)
        raise Exception(f"Max retries exceeded {self.model}")


    def _process_posology(self, drug_name, form,  posology) -> str:
        '''Use GPT-4 to process the posology'''
        backoff_factor=1.0
        for attempt in range(self.retries):
            try:
                response = client.chat.completions.create(model=self.model,
                                        messages=[{"role": "system", "content": ""},
                                                {"role": "user", "content":  USER_PROCESS_POSOLOGY.format(drug_name=drug_name, drug_form=form, posology=posology)}],
                                        max_tokens=4000,
                                        temperature = 0)
                cleaned_text = response.choices[0].message.content
                if cleaned_text.startswith("<<ALL>>"):
                    return posology
                
                return cleaned_text
            except Exception as e:
                print(f"Failed to process text with GPT-4 _process_posology: {e}")
                wait = backoff_factor * (2 ** attempt)
                time.sleep(wait)
        raise Exception(f"Max retries exceeded {self.model}")


    def _process_contraindications(self, drug_name, form,  indications) -> str:
        '''Use GPT-4 to process the contraindications'''

        try:
            response = client.chat.completions.create(model=self.model,
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_PROCESS_CONTRAINDICATIONS.format(drug_name=drug_name, drug_form=form, indications=indications)}],
                                    max_tokens=4000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            if cleaned_text.startswith("<<ALL>>"):
                return indications
            
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4 _process_contraindications: {e}")
            return None


    def _process_cross_reactions(self, drug_name, active_ingredients,  special_warnings) -> str:
        '''Use GPT-4 to process the cross reactions'''
        m = "gpt-4o"
        backoff_factor=1.0
        for attempt in range(self.retries):
            try:
                response = client.chat.completions.create(model=m,
                                        messages=[{"role": "system", "content": ""},
                                                {"role": "user", "content":  USER_PROCESS_CROSS_REACTIONS.format(drug_name=drug_name, active_ingredients=active_ingredients, text=special_warnings)}],
                                        max_tokens=4000,
                                        temperature = 0)
                cleaned_text = response.choices[0].message.content
                i = cleaned_text.find("```json")
                if i ==-1:
                    return {"description":"", "incidence":"", "da": "", "cross_sensitive_drugs":[]}
                else:
                    j = cleaned_text.rfind("```")
                    cleaned_text = cleaned_text[i + 7:j]
                    if len(cleaned_text) <10:
                        return {"description":"", "incidence":"", "da": "", "cross_sensitive_drugs":[]}
                    
                    # JSON in the following format
                    # { 
                    #  "description": "Provide a concise overview (1-2 paragraphs) of clinical/theoretical evidence supporting the possibility of cross-sensitivity between drugs. Include any warnings or alerts relevant to this issue.", 
                    #  "incidence": "State the reported cross-sensitivity rate. Use values like: At least X%|Up to X%|X%|X-Y%|Common|Uncommon|Rare|Single case reports|Theoretical", 
                    #  "da": "Specify the drug active ingredient causing cross-reactivity", 
                    #  "cross_sensitive_drugs": [{"ai": "List all potential active ingredients from other drugs that cause cross-reaction. Names must be reported exactly as they appear in the text. Singularized."}]
                    # }
                    res= json.loads(cleaned_text, strict=False)
                    if 'cross_sensitive_drugs' in res and len(res['cross_sensitive_drugs'])==0:
                        return {"description":"", "incidence":"", "da": "", "cross_sensitive_drugs":[]}
                    return res
            except Exception as e:
                print(traceback.format_exc())
                print(f"Failed to process text with GPT-4 _process_cross_reactions: {e}")
                wait = backoff_factor * (2 ** attempt)
                time.sleep(wait)
        raise Exception(f"Max retries exceeded {self.model}")

    def _process_drug_incompatibilities(self, drug_name, form,  incompatibilities) -> str:
        '''Use GPT-4 to process the drug interactions'''

        try:
            response = client.chat.completions.create(model=self.model,
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_PROCESS_INCOMPATIBILITIES.format(drug_name=drug_name, drug_form=form, incompatibilities=incompatibilities)}],
                                    max_tokens=4000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            if cleaned_text.startswith("<<ALL>>"):
                return incompatibilities
            
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4: {e}")
            return None

    def _process_drug_interactions(self, drug_name, form,  interactions) -> str:
        '''Use GPT-4 to process the drug interactions _process_drug_incompatibilities'''

        try:
            response = client.chat.completions.create(model=self.model,
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_PROCESS_INTERACTIONS.format(drug_name=drug_name, drug_form=form, interactions=interactions)}],
                                    max_tokens=4000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            if cleaned_text.startswith("<<ALL>>"):
                return interactions
            
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4 _process_drug_interactions: {e}")
            return None

    # Write or update the csv with the new leaflets data
    def write_csv(self,leaflet_list):
        data = []
        drug_codes = set()  # To keep track of drug codes written to CSV
        for leaflet in leaflet_list:
            data.append({
                "drug_code": leaflet.drug_code,
                "drug_name": leaflet.drug_name,
                "atc": leaflet.atc,
                "drug_form": leaflet.drug_form,
                "composition": leaflet.composition,
                "excipients": leaflet.PharmaInfo["excipients"],
                "therapeutic_indications": leaflet.clinicalInfo["therapeutic_indications"],
                "posology": leaflet.clinicalInfo["posology"],
                "cross_reactivity": str(leaflet.cross_reaction),
                "contraindications": leaflet.clinicalInfo["contraindications"],
                "special_warnings": leaflet.clinicalInfo["special_warnings"],
                "drug_interactions": leaflet.clinicalInfo["drug_interactions"],
                "pregnancy_info": leaflet.clinicalInfo["pregnancy_info"],
                "driving_effects": leaflet.clinicalInfo["driving_effects"],
                "side_effects": leaflet.clinicalInfo["side_effects"],
                "over_dose": leaflet.clinicalInfo["over_dose"],
                "incompatibilities": leaflet.PharmaInfo["incompatibilities"],
                "leaflet": leaflet.leaflet
                #,
                #"excipients_tokens": leaflet.excipients_tokens,
                #"special_warnings_tokens" : leaflet.special_warnings_tokens,
                #"posology_tokens" : leaflet.posology_tokens,
                #"contraindications_tokens" : leaflet.contraindications_tokens,
                #"drug_interactions_tokens" : leaflet.drug_interactions_tokens,
                #"incompatibilities_tokens" : leaflet.incompatibilities_tokens,
                #"multiple_forms" : leaflet.multiple_forms
            })
            drug_codes.add(leaflet.drug_code)

        for index, row in self.df.iterrows():
            drug_code = row['drug_code']
            found = False
            for l in leaflet_list:
                if l.drug_code == drug_code:
                    found = True
                    break
            if not found:
                print("drug_code", drug_code, "NOT FOUND")

        print("LEN DATA", len(data), len(drug_codes), len(leaflet_list))
        # Create a new DataFrame using the processed data
        df = pd.DataFrame(data)

        # We check if the CSV already exists
        file_exists = os.path.isfile('leaflet_info.csv')

        # Write the DataFrame as CSV
        df.to_csv('leaflet_info.csv', mode='a' if file_exists else 'w', header=not file_exists, index=False, encoding='utf-8')    

        # Update the 'preprocessed' column in self.df for the the drug codes written in the CSV file
        #self.df.loc[self.df['drug_code'].isin(drug_codes), 'preprocessed'] = "OK"
        for drug_code in drug_codes:
            self.df.loc[self.df['drug_code'] == drug_code, 'preprocessed'] = "OK"

        # We override the original dataset
        self.df.to_excel(self.dataset_name, index=False)

if __name__ == "__main__":
    start_time = time.time()
    preprocessor = LeafletInfoPreProcessor(model="gpt-4o")    
    leaflet_infos = preprocessor.parallel_process_leaflets()

    
    preprocessor.write_csv(leaflet_infos)
    end_time = time.time()
    print(f"TOTAL TIME FOR DRUGS: {end_time - start_time:.2f} seconds")

    
    print("INITIALIZE SYNONYMS")
    start_time = time.time()
    preprocessor.save_dictionary()
    end_time = time.time()
    print(f"TOTAL TIME FOR SYNONYMS INITIALIZATION: {end_time - start_time:.2f} seconds")
    
    print("POPULATE SYNONYMS")
    start_time = time.time()
    preprocessor.process_synonyms()
    end_time = time.time()
    print(f"TOTAL TIME FOR INGREDIENTS: {end_time - start_time:.2f} seconds")
