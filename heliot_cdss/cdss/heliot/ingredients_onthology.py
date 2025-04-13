import pandas as pd
import time

# Class to handle drug synonyms
class SynonymManager:
    def __init__(self, initial_data_path):
        """
        Initialize SynonymManager loading the synonyms dataset.
        
        Parameters:
        - initial_data_path: path of the synonyms cvs file.
        """
        try:
            self.df = pd.read_csv(initial_data_path,dtype=str)
        except:
            self.df = pd.read_csv(initial_data_path, delimiter=';',dtype=str)
            
        self.synonym_to_ingredient = {}
        self._populate_synonym_dict()

    def _populate_synonym_dict(self):
        """
        Populate the dictionary starting from the DataFrame.
        """
        for idx, row in self.df.iterrows():
            synonyms = row['synonyms']
            if pd.notna(synonyms):
                for synonym in synonyms.split('#'):
                    self.synonym_to_ingredient[synonym] = row['english_name']

    def update_dataset(self, new_data_path):
        """
        Update the dataset and the dictionary with new data.
        
        Parameters:
        - new_data_path: path of the CVS to process to add new synonyms.
        """
        new_df = pd.read_csv(new_data_path)
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        for idx, row in new_df.iterrows():
            synonyms = row['synonyms']
            if pd.notna(synonyms):
                for synonym in synonyms.split('#'):
                    self.synonym_to_ingredient[synonym] = row['english_name']

    def find_standard_name(self, synonym):
        """
        Look for the standard name of the ingredient starting from its synonym.
        
        Parameters:
        - synonym: synonym for the ingredient to look for.

        Returns:
        - Standard ingredient name for the synonym or None it didn't find one.
        """
        return self.synonym_to_ingredient.get(synonym, synonym)

    def find_standard_names(self, synonyms):
        """
        Look for the standard name of the ingredient starting from its synonym.
        
        Parameters:
        - synonym: synonym for the ingredient to look for.

        Returns:
        - Standard ingredient name for the synonym or None it didn't find one.
        """
        res = []
        for s in synonyms:
            res.append({"n":s, "t":self.synonym_to_ingredient.get(s, s)})
        return res

    def add_ingredient(self, ingredient, english_name, type_, synonyms):
        """
        Add a new ingredient and update the dictionary.
        
        Parameters:
        - ingredient: ingredient name.
        - english_name: English name of the ingredient.
        - type_: Ingredient type.
        - synonyms: synonym list of the ingredient.
        """
        if synonyms is None:
            synonyms =[]
        new_row = {
            'ingredient': ingredient, 
            'english_name': english_name, 
            'type': type_, 
            'synonyms': '#'.join(synonyms)
        }
        
        self.df = self.df.append(new_row, ignore_index=True)
        for synonym in synonyms:
            self.synonym_to_ingredient[synonym] = ingredient

    

if __name__ == "__main__":
    synonym_manager = SynonymManager('ingredients_synonyms.csv')

    # Look for the standard name given its synonym
    start_time = time.time()
    standard_name = synonym_manager.find_standard_name('combreto')
    end_time = time.time()
    print(standard_name)
    print(f"TOTAL TIME to SEARCH: {end_time - start_time:.2f} seconds")
