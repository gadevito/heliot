import sqlalchemy as sa
import pandas as pd
import io

#
# Load drugs from DB and leaflets from TDT.xml file. Finally, it writes the dataset file containing drugs and leaflets' references.
#
class DatasetBuilder:
    def __init__(self):
        self.engine = sa.create_engine('postgresql://postgres:ppa2vms@localhost:5433/gabrieledevito')

        self.records = pd.read_xml('TDT.xml',dtype={"FDI_T431": "string", "FDI_T218": "string", "FDI_T219": "string", "FDI_T220": "string", "FDI_T235": "string"})
        print(self.records.count())

    #
    # Find the leafleat for the drug identified by 'code'
    #
    def findLeaflet(self, code):

        row= self.records.loc[self.records['FDI_T218'] == code]
        
        for name in row['FDI_T235']:
            return name

    #
    # Read data from db and write all in an excel file
    #
    def readData(self):
        query = """select d.drug_code, f.countable, f.solvent, f.senza_fustella, f.drug_name, f.drug_dosage, 
                          f.drug_form_code, f.drug_form_descr, f.drug_form_full_descr, f.abstract_drug_code, f.abstract_drug, 
                          f.num_units, f.commercial_state, f.cod_tipo_prodotto, f.desc_tipo_prodotto, a.code as active_princ_code, 
                          a.description as active_princ_descr,d.atc_code, ' ' as leaflet 
                    from full_farmadati_view as f, drug_view as d, active_principle_view as a
                    where f.code = d.drug_code and d.active_principle_code = a.code"""
        sql = sa.text(query) 

        df = pd.read_sql_query(sql, self.engine)

        i = 0
        for index, row in df.iterrows():
            l =self.findLeaflet(row['drug_code'])
            df.at[index,'leaflet'] = l
            i = i+1
            if i % 100 == 0:
                print(i)
        print(df)
        df.to_excel("dataset.xlsx") 

def main():
    c = DatasetBuilder()
    c.readData()

if __name__ == "__main__":
    main()