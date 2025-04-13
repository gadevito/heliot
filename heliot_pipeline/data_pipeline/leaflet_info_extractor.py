#import tiledb.vector_search as vs
#from tiledb.vector_search.utils import *

from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
import tiktoken

import pandas as pd

# Utility class to store the leaflet data
class LeafletInfo:
    def __init__(self):
        self.drug_code = ""
        self.drug_name= ""
        self.drug_form=""
        self.leaflet = ""
        self.atc = ""
        self.composition =""
        self.clinicalInfo = {"full_text": "", "therapeutic_indications": "", "posology": "", "contraindications": "", "special_warnings": "", "drug_interactions": "", "pregnancy_info": "", "driving_effects": "","side_effects" :"", "over_dose":""}
        self.PharmaInfo = {"full_text":"", "excipients": "", "incompatibilities": ""}
        self.cross_reaction = {}
        self.ingredients=""
        self.excipients_tokens = 0
        self.special_warnings_tokens = 0
        self.posology_tokens = 0 
        self.contraindications_tokens = 0
        self.drug_interactions_tokens = 0
        self.incompatibilities_tokens = 0
        self.multiple_forms = 0

    def __str__(self):
        ecc = self.PharmaInfo["excipients"]
        sp = self.clinicalInfo["special_warnings"]
        return (f"LeafletInfo(\n"
                f"  drug_code: {self.drug_code}\n"
                f"  drug_name: {self.drug_name}\n"
                f"  drug_form: {self.drug_form}\n"
                f"  atc: {self.atc}\n"
                f"  leaflet: {self.leaflet}\n"
                f"  composition: {self.composition}\n"
                f"  excipients: {ecc}\n"
                f"  special_warnings: {sp}\n"
                f")")

# Class to extract info from leaflets
class LeafletInfoExtractor:
    def __init__(self, path: str, glob = "**/[!.]*", exclude =[], recursive = True):
        self.path = path
        self.glob = glob
        self.exclude = exclude
        self.recursive = recursive
        #self.encoding = tiktoken.get_encoding("cl100k_base")
        
    
    def extractDrugName(self, text: str):
        i = text.find("01.0 DENOMINAZIONE DEL MEDICINALE")
        j = text.find("02.0 COMPOSIZIONE QUALITATIVA E QUANTITATIVA")
       
        if i != -1 and j != -1:
            i += 33
            return text[i:j-2]
        return ""

    def extractIngredientsFromComposition(self,text: str):
        i = text.lower().find("eccipient")
        if i!=-1:
            return text[0:i]
        return text

    def extractTherapeuticInfo(self, text:str):
        i = text.find("04.1 Indicazioni terapeutiche")
        j = text.find("04.2 Posologia e modo di somministrazione")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractPosology(self, text:str):
        i = text.find("04.2 Posologia e modo di somministrazione")
        j = text.find("04.3 Controindicazioni")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractPregnancyInfo(self, text: str):
        i = text.find("04.6 Gravidanza ed allattamento")
        j = text.find("04.7 Effetti sulla capacita' di guidare veicoli e sull'uso di macchinari")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractDrivingEffects(self, text:str):
        i = text.find("04.7 Effetti sulla capacita' di guidare veicoli e sull'uso di macchinari")
        j = text.find("04.8 Effetti indesiderati")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractContraindications(self, text: str):
        i = text.find("04.3 Controindicazioni")
        j = text.find("04.4 Avvertenze speciali e opportune precauzioni d'impiego")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractSpecialWarnings(self, text: str):
        i = text.find("04.4 Avvertenze speciali e opportune precauzioni d'impiego")
        j = text.find("04.5 Interazioni con altri medicinali e altre forme di interazione")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractInteractions(self, text: str):
        i = text.find("04.5 Interazioni con altri medicinali e altre forme di interazione")
        j = text.find("04.6 Gravidanza ed allattamento")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractPregnancyInfo(self, text: str):
        i = text.find("04.6 Gravidanza ed allattamento")
        j = text.find("04.7 Effetti sulla capacita' di guidare veicoli e sull'uso di macchinari")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractSideEffects(self, text: str):
        i = text.find("04.8 Effetti indesiderati")
        j = text.find("04.9 Sovradosaggio")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""        

    def extractOverDoseInfo(self, text: str):
        i = text.find("04.9 Sovradosaggio")
        j = text.find("05.0 PROPRIETA' FARMACOLOGICHE")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractComposition(self,text: str):
        i = text.find("02.0 COMPOSIZIONE QUALITATIVA E QUANTITATIVA")
        j = text.find("03.0 FORMA FARMACEUTICA")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractClinicalInfo(self,text: str):
        i = text.find("04.0 INFORMAZIONI CLINICHE")
        j = text.find("05.0 PROPRIETA' FARMACOLOGICHE")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""

    def extractPharmaInfo(self,text: str):
        i = text.find("06.0 INFORMAZIONI FARMACEUTICHE")
        j = text.find("07.0 TITOLARE DELL'AUTORIZZAZIONE ALL'IMMISSIONE IN COMMERCIO")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""    

    def extractExcipientsFromPharmaInfo(self,text: str):
        i = text.find("06.1 Eccipienti")
        j = text.find("06.2 Incompatibilita")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""      

    def extractIncompatibilities(self, text: str):
        i = text.find("06.2 Incompatibilita")
        j = text.find("06.3 Periodo di validita")
        if i != -1 and j != -1:
            return text[i:j-2]
        return ""      

    def loadLeafletFile(self,drug_code="", drug_name="", drug_form="", leaflet="") -> LeafletInfo:
        #print("CHIAMATO con", self.path+"/"+leaflet,drug_code, drug_name, drug_form)
        return self._loadLeafletFile(self.path+"/"+leaflet,drug_code, drug_name, drug_form)

    def _loadLeafletFile(self,file_path: str, drug_code="", drug_name="", drug_form="") -> LeafletInfo:
        text =""
        # c'era anche utf-8
        for encoding in ['latin-1', 'iso-8859-1']:  # Common encoding list
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    html_content = file.read()        
                    soup = BeautifulSoup(html_content, 'html.parser')
                    text = soup.get_text()
                    text = text.replace("-  [Vedi Indice]","")
                    i = text.find("01.0 ",200)
                    if i != -1:
                        text = text[i:]
                    
                    break
            except UnicodeDecodeError:
                print("Problema di encoding", encoding)
                continue
        l = LeafletInfo()
        if len(drug_name) == 0:
            drug_name = self.extractDrugName(text)
        l.drug_code = drug_code
        l.drug_name = drug_name
        l.drug_form = drug_form
        l.composition = self.extractComposition(text)
        l.ingredients = self.extractIngredientsFromComposition(l.composition)
        clinicalInfo = self.extractClinicalInfo(text)
        l.clinicalInfo["full_text"] = clinicalInfo
        l.clinicalInfo["contraindications"] = self.extractContraindications(clinicalInfo)
        l.clinicalInfo["special_warnings"] = self.extractSpecialWarnings(clinicalInfo)
        l.clinicalInfo["drug_interactions"] = self.extractInteractions(clinicalInfo)
        l.clinicalInfo["pregnancy_info"] = self.extractPregnancyInfo(clinicalInfo)
        l.clinicalInfo["therapeutic_indications"] = self.extractTherapeuticInfo(clinicalInfo)
        l.clinicalInfo["driving_effects"] = self.extractDrivingEffects(clinicalInfo)
        l.clinicalInfo["posology"] = self.extractPosology(clinicalInfo)
        l.clinicalInfo["pregnancy_info"] = self.extractPregnancyInfo(clinicalInfo)
        l.clinicalInfo["side_effects"] = self.extractSideEffects(clinicalInfo)
        l.clinicalInfo["over_dose"] = self.extractOverDoseInfo(clinicalInfo)

        PharmaInfo = self.extractPharmaInfo(text)
        l.PharmaInfo["full_text"] = PharmaInfo
        l.PharmaInfo["excipients"] = self.extractExcipientsFromPharmaInfo(PharmaInfo)
        l.PharmaInfo["incompatibilities"] = self.extractIncompatibilities(PharmaInfo)

        ix = file_path.find("/",2)
        if ix != -1:
            l.leaflet = file_path[ix+1:]
        else:
            l.leaflet = file_path
        #print(l.leaflet)
        return l


    def process(self) -> List[LeafletInfo]:
        p = Path(self.path)
        res = []
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: '{self.path}'")
        if not p.is_dir():
            raise ValueError(f"Expected directory, got file: '{self.path}'")

        paths = p.rglob(self.glob) if self.recursive else p.glob(self.glob)
        items = [
                path
                for path in paths
                if not (self.exclude and any(path.match(self.glob) for self.glob in self.exclude))
                and path.is_file()
            ]
        for item in items:
            #print("APRO:", item)
            res.append(self._loadLeafletFile("./"+str(item)))
        
        return res
            
    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        num_tokens = len(self.encoding.encode(string))
        return num_tokens

'''
text = loadLeafletFile("./documents/0069795.htm")
comp = extractComposition(text)
print("*********>\n COMPOSIZIONE\n", comp, "\n*****")

pharma = extractPharmaInfo(text)

excipients = extractExcipientsFromPharmaInfo(pharma)

print("EXCIPIENTS===>>\n",excipients, "\n********<<")


text = loadLeafletFile("./documents/0086438.htm")
comp = extractComposition(text)
print("*********>\n COMPOSIZIONE\n", comp, "\n*****")

pharma = extractPharmaInfo(text)

excipients = extractExcipientsFromPharmaInfo(pharma)

print("EXCIPIENTS===>>\n",excipients, "\n********<<")
'''

'''
lproc = LeafletProcessor("./documents")
res = lproc.process()

total_tokens = 0
df = pd.read_excel("patients_complete.xlsx")

def check_leaflet_existence(leaflet_value):
    
    # Controlla se il valore del leaflet esiste nella colonna 'leaflet'
    exists = leaflet_value in df['leaflet'].values
    
    return exists


total_comp_exc_tokens = 0
num_occ =0
max_leaflet_lenght = 0
smax_leaflet_lenght = 0


for r in res:
    if check_leaflet_existence(r.leaflet):
        compl = lproc.num_tokens_from_string(r.composition)
        clinl = lproc.num_tokens_from_string(r.clinicalInfo["full_text"])
        pharml = lproc.num_tokens_from_string(r.PharmaInfo["full_text"])
        total_tokens += compl
        total_tokens += clinl
        total_tokens += pharml

        

        pos = lproc.num_tokens_from_string(r.clinicalInfo["posology"])
        spec = lproc.num_tokens_from_string(r.clinicalInfo["special_warnings"])
        exc = lproc.num_tokens_from_string(r.PharmaInfo["excipients"])



        total_comp_exc_tokens += pos

        total_comp_exc_tokens += spec

        total_comp_exc_tokens += exc

        if compl + clinl + pharml > 8000:
            max_leaflet_lenght += compl + clinl + pharml

        if pos + spec + exc > smax_leaflet_lenght:
            smax_leaflet_lenght = pos + spec + exc

         
 
        #if compl > 10000 or clinl > 10000 or pharml > 10000:
        #    print("LEAFLET",r.leaflet, compl, clinl, pharml)
        #    num_occ +=1

        if pos > 10000 or spec > 10000 or exc > 10000:
            print("LEAFLET",r.leaflet, pos, spec, exc)
            num_occ +=1



    #print(r.drug_name)
    #print("DIM composition", len(r.composition), "tokens:", lproc.num_tokens_from_string(r.composition))
    #print("DIM clinicalInfo", len(r.clinicalInfo), "tokens:", lproc.num_tokens_from_string(r.clinicalInfo))
    #print("DIM pharmaInfo", len(r.PharmaInfo), "tokens:", lproc.num_tokens_from_string(r.PharmaInfo))

print("TOTAL TOKENS", total_tokens, "AVG tokens per leaflet", total_tokens/len(res))
print("MIN_TOTAL_TOKENS", total_comp_exc_tokens)
print("NUM OCC.", num_occ)

print("MAX LEAFLET SIZE > 8k", max_leaflet_lenght)
print("MAX LEAFLET SIZE WHEN REDUCED", smax_leaflet_lenght)
'''