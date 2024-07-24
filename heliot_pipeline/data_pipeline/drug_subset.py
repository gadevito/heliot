import pandas as pd

# Read the drugs dataset
df = pd.read_excel('drugs.xslx', dtype={'drug_code': str, 'leaflet': str})

# Filtering rows where 'leaflet' is not empy
df_filtered = df.dropna(subset=['leaflet'])

# Select 1000 rows randomly
df_sampled = df_filtered.sample(n=1000, random_state=1)  # random_state to ensure reproducibility 

# Save the result
df_sampled.to_excel('drugs_subset.xlsx', index=False)