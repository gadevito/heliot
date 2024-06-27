import pandas as pd
from bs4 import BeautifulSoup
import os
from openai import OpenAI
import concurrent.futures

# Initialize the OPENAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

map = {}
count = 0
executed =[]

def extract_content_from_section(file_path, section_id):
    encoding_success = False
    # We try with different encodings in case of errors
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:  # Common encoding list
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                html_content = file.read()        
                soup = BeautifulSoup(html_content, 'html.parser')
                encoding_success = True
                break
        except UnicodeDecodeError:
            continue

    if not encoding_success:
        print(f"Unable to decode {file_path} with the attempted encodings.")
        return

    sections = soup.find_all('a', {'name': section_id})
    
    if sections:
        text_content = ''
        for section in sections:
            current_elem = section.find_next('p')
            while current_elem and current_elem.name != 'h2':
                text = current_elem.get_text()
                i = text.find("03.0 FORMA FARMACEUTICA")
                if i != -1:
                    text = text[0:i]
                text = text.replace("[Vedi Indice]","")
                if len(text)>0:
                    text_content += text + '\n'
                if i != -1:
                    break
                current_elem = current_elem.find_next_sibling()
        return text_content
    else:
        return None

#
# This function process the leaflet file, looking for the 'Excipients' section.
#
def extract_excipients(file_html):
    encoding_success = False

    # Prova con diversi encoding in caso di errori
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:  
        try:
            with open(file_html, 'r', encoding=encoding) as file:
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')
                encoding_success = True
                break
        except UnicodeDecodeError:
            continue

    if not encoding_success:
        print(f"Error in decoding {file_html} file.")
        return

    sotto_titoli = soup.find_all('a', attrs={'name': lambda x: x and x.startswith('SottoTitolo_03')})
    if not sotto_titoli:
        print("No 'SottoTitolo_03' found.")
        return None

    sotto_titolo = sotto_titoli[0]
    elements = []
    end_found = False

    current_element = sotto_titolo.find_next()
    while current_element and not end_found:
        if current_element.name == 'h3':
            end_found = True
        else:
            #print("#"+current_element.name+"#", current_element.text.strip())
            if current_element.text.strip():
                text = current_element.get_text(separator=' ', strip=True)
                i = text.find("06.2 Incompatibilita")
                if i != -1:
                    text = text[0:i]
                text = text.replace("[Vedi Indice]","")
                if len(text) > 0:
                    elements.append(text)
                if i != -1:
                    break
        current_element = current_element.find_next()

    if elements:
        excipient_text = ' '.join(elements)
        if excipient_text.strip().startswith("Vedere ") or excipient_text.strip().startswith("-----"):
            #print("Vai a Titolo_02")
            excipient_text = extract_content_from_section(file_html, "Titolo_02")
        #print(file_html, "Eccipienti trovati:", excipient_text)
        return excipient_text
    else:
        print("No valid paragraph trovato.", file_html)
        return None

#
# This function processes the text extracted from the leaflet file using GPT-4
#
def gpt4_process(text, file):
    val = map.get(file)
    if val is not None:
        return val

    SYSTEM_BASE= """Act as an expert physician.

Your task is to provide the list of the excipients starting from the text I'll provide.

The output must be a comma-separated list, but it must be splittable using text.split(",") in python.
We are interested only in the excipients names, not in quantities or acronyms.
For example:
- if an excipient is followed by a number or an acronym, you must consider only its name. So, for "Povidone 1000" provide "Povidone", and for "Povidone X 1000" provide only "Povidone";
- If a name already contains ",", replace "," with ".". 

Answer only with the list.
    """

    USER_BASE ="""TEXT:{testo}"""
    try:
        response = client.chat.completions.create(model="gpt-4-turbo",
                                messages=[{"role": "system", "content": SYSTEM_BASE},
                                        {"role": "user", "content":  USER_BASE.format(testo=text)}],
                                max_tokens=1000,
                                temperature = 0)
        cleaned_text = response.choices[0].message.content
        map[file] = cleaned_text
        return cleaned_text
    except Exception as e:
        print(f"Failed to process text with GPT-4: {e}")
        return None

def process_row(row):
    if pd.notna(row[0]):  # Accedi all'unico elemento della tupla
        return gpt4_process(extract_excipients("./leaflet/"+row[0]), row[0])
    else:
        return None

# Load the original dataset
df = pd.read_excel('dataset.xlsx', dtype='string')

print("Dataset read....")
processed_count = 0
with concurrent.futures.ThreadPoolExecutor(15) as executor:
    results = []

    for result in executor.map(process_row, df[['leaflet']].itertuples(index=False, name='Leaflet')):
        results.append(result)
        processed_count += 1

        # Stampa lo stato ogni 100 righe processate
        if processed_count % 100 == 0:
            print(f"{processed_count} processed rows")

df['eccipienti'] = results

# Add the new column 'eccipienti' for excipients
# Note: We may process files in parallel, but for now we use the sequential strategy
#df['eccipienti'] = df['leaflet'].parallel_apply(lambda x: gpt4_process(extract_excipients("./leaflet/"+x), x) if pd.notna(x) else None)

# Save the new dataset
df.to_excel('drugs.xlsx', index=False)