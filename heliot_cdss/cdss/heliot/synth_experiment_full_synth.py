import pandas as pd
import requests
import json
import time
from tqdm import tqdm

# Process the HELIOT service response
def process_response(response):
    result_text = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if "data: {\"message\":" in decoded_line:
                j = decoded_line.rfind("\"}")
                decoded_line = decoded_line[5:]
                mess = json.loads(decoded_line)
                decoded_line = mess['message']
            
            if not "data: {\"input\":" in decoded_line:
                result_text += decoded_line
    
    try:
        result_json = json.loads(result_text)
        return result_json
    except:
        return None

def main():
    # 1. Read the patients_synthetic dataset
    df = pd.read_excel('patients_synthetic.xlsx', dtype={'drug_code': str, 'leaflet': str, 'patient_id': str})
    
    # List for the results 
    results = []
    
    # URL of the HELIO service
    url = "http://localhost:8000/api/allergy_check_enhanced"
    
    # 2. Process each row
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing results..."):

        
        payload = {
            "patient_id": row['patient_id'],
            "drug_code": row['drug_code'],
            "clinical_notes": row['clinical_note'],
            "store": False  
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, stream=False)
            end = time.time()
            
            if response.status_code == 200:
                result_json = process_response(response)
                
                if result_json:
                    # Add all the synthetic_patients dataset fields
                    result_row = row.to_dict()
                    
                    # Add the result fields
                    result_row['timing'] = end - start_time
                    result_row['response'] = result_json.get('a', '')
                    result_row['classification_resp'] = result_json.get('r', '')
                    result_row['reaction_resp'] = result_json.get('rt', '')

                    results.append(result_row)
            else:
                print(f"Error in request for patient_id {row['patient_id']}: {response.status_code}")
                raise
                
        except Exception as e:
            print(f"Error for patient_id {row['patient_id']}: {str(e)}")
    
    # 3. Create a new DataFrame with results
    results_df = pd.DataFrame(results)
    
    # Save the Excel
    output_filename = 'results_full_synth.xlsx'
    results_df.to_excel(output_filename, index=False)
    print(f"Risultati salvati in {output_filename}")

if __name__ == "__main__":
    main()