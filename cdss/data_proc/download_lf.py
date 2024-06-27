from urllib.request import urlretrieve
import pandas as pd
from pathlib import Path
import os

ACCESS_KEY = os.getenv('FARMADATI_ACCESS_KEY')
#
# Load drugs from DB and leaflets from TDT.xml file. Finally, it writes the dataset file containing drugs and leaflets' references.
#
class DownloadLeaflet:
    def __init__(self):
        self.df = pd.read_excel('dataset.xlsx', dtype={'drug_code': "string",
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
        for col in self.df.columns:
            print(col)
        self.df = self.df.loc[self.df['leaflet'] != ""]
        self.df = self.df.loc[self.df['leaflet'] != " "]

    def download(self):
        i = 0
        count_new = 0
        count_exist = 0
        for index, row in self.df.iterrows():
            l = row['leaflet']
            print(l)
            url = f"https://ws.farmadati.it/WS_DOC/GetDoc.aspx?accesskey={ACCESS_KEY}&tipodoc=T&nomefile={l}"
            filename = "./leaflet/"+l
            ff = Path(filename)
            if not ff.exists():
                count_new +=1
                print("scarico", filename)
                urlretrieve(url, filename)
            else:
                count_exist +=1
                print("File alreasy exists", filename)
            i = i+1
            if i % 100 == 0:
                print(i, index)
        print("NEW ", count_new, "PRESENT", count_exist)
        
def main():
    c = DownloadLeaflet()
    c.download()
    p = Path(r'./leaflet').glob('**/*')
    files = [x for x in p if x.is_file()]
    print("NUMERO FILES", len(files))
    
if __name__ == "__main__":
    main()