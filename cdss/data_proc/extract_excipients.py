import pandas as pd
import re

# Carica il dataset dei farmaci
drugs = pd.read_excel('drugs.xlsx')

def clean_name(allergy):
    if pd.isnull(allergy) or allergy == "":
        return None
    # Rimuovere tutto ciò che segue numeri, percentuali o parentesi
    orig = allergy

    allergy = allergy.upper()
    allergy = allergy.replace("1,2","1-2")
    '''
    allergy = allergy.replace("A BASSO GRADO DI SOSTITUZIONE","").replace("A BASSA SOSTITUZIONE","")
    allergy = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', allergy)  # Rimuove il contenuto tra parentesi tonde e quadre
    allergy = allergy.replace("%","").replace("[", "").replace("]","").replace("(","").replace(")","")
    allergy = allergy.replace("DI TIPO","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("5","").replace("7","").replace("8","").replace("9","")
    allergy = allergy.replace("MPA.S","")
    allergy = allergy.replace(" TIPO ","")
    #allergy = allergy.replace(" MG","")
    allergy = re.sub(r'\d+[,.]?\d*\s*mg', '', allergy, flags=re.IGNORECASE)  # Rimuove le quantità in mg
    allergy = re.sub(r'\bE\d+', '', allergy, flags=re.IGNORECASE)  # Rimuove i codici che iniziano per 'E' seguiti da numeri
    '''

    l = allergy.split(",")
    if "1" in l:
        print("ORIG", orig)
    
    if allergy == "E 171":
        allergy = "BIOSSIDO DI TITANIO"
    elif allergy == "E464":
        allergy = "IPROMELLOSA"

    return allergy

# Funzione per pulire e separare gli eccipienti
def clean_and_extract_excipients(excipient_string):
    if pd.isna(excipient_string):
        return []
    # Rimuovi testi tra parentesi e caratteri speciali, tranne la virgola
    cleaned_string = clean_name(excipient_string) 
    excipients = cleaned_string.split(',')
    # Pulizia ulteriore degli spazi inutili e conversione ad uppercase
    return [excipient.strip().upper() for excipient in excipients if excipient.strip()]

# Estrai e pulisci gli eccipienti, unendo tutti in un unico set per unicità
unique_excipients = set()
drugs['eccipienti'].dropna().apply(lambda x: unique_excipients.update(clean_and_extract_excipients(x)))

# Converti il set in lista per la creazione del DataFrame
unique_excipients_list = list(unique_excipients)

# Creazione del DataFrame per gli eccipienti
excipients_df = pd.DataFrame(unique_excipients_list, columns=['Excipient'])

# Salvataggio del DataFrame in un file Excel
excipients_df.to_excel('excipients.xlsx', index=False)

