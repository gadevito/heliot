import pandas as pd
import json

# Drug Classes
drug_classes = {
    "Opioids": [
        "N02AB03", "N02AA01", "N02AA05", "N02AB02", "N02AX02", "N02AX06",
        "N02AA03", "N02AE01", "N02AA55", "N02AJ14", "N02AJ06", "N02AJ13",
        "N02AA59", "N02AJ08"
    ],
    "Antibiotics": [
        "J01CA04", "J01CA01", "J01CA12", "J01DB04", "J01DD04", "J01DH02",
        "J01DC02", "J01DH51"
    ],
    "NSAID": [
        "M01AE01", "M01AE02", "M01AH01", "M01AB05", "M01AB01", "M01AH05"
    ],
    "Diuretics": [
        "C03CA01", "C03CA04"
    ],
    "Antiplatelet agents": [
        "B01AC04", "B01AC06", "B01AC24", "B01AC22"
    ]
}

# Load the dataset
df = pd.read_excel('patients_synthetic.xlsx')

# Function to assign drug classes
def get_drug_class(atc_code):
    for class_name, atc_list in drug_classes.items():
        if atc_code in atc_list:
            return class_name
    return "Other"

# Add the column drug_class
df['drug_class'] = df['prescribed_atc'].apply(get_drug_class)

# Compute statistics for classification_descr
print("\nNo of cases by classification:")
print("----------------------------------------")
classification_counts = df['classification_descr'].value_counts()
classification_percentages = df['classification_descr'].value_counts(normalize=True).mul(100).round(1)
classification_stats = pd.DataFrame({
    'Count': classification_counts,
    'Percentage': classification_percentages
})
print(classification_stats)

# Calcolo statistiche per drug_class
print("\nNo of cases by drug class:")
print("-------------------------------")
drug_class_counts = df['drug_class'].value_counts()
drug_class_percentages = df['drug_class'].value_counts(normalize=True).mul(100).round(1)
drug_class_stats = pd.DataFrame({
    'Count': drug_class_counts,
    'Percentage': drug_class_percentages
})
print(drug_class_stats)

# Calcolo statistiche incrociate
print("\nNo of cases di casi by classification and drug_class:")
print("----------------------------------------------------")
cross_counts = pd.crosstab(df['classification_descr'], df['drug_class'], margins=True)
print("\nTotals:")
print(cross_counts)

# Calcolo percentuali per riga
cross_percentages = pd.crosstab(df['classification_descr'], df['drug_class'], normalize='index').mul(100).round(1)
print("\nPercentages by row (%):")
print(cross_percentages)

# Salvataggio dei risultati in Excel
with pd.ExcelWriter('drug_statistics.xlsx') as writer:
    # Foglio 1: Statistiche per classification_descr
    classification_stats.to_excel(writer, sheet_name='Classification Stats')
    
    # Foglio 2: Statistiche per drug_class
    drug_class_stats.to_excel(writer, sheet_name='Drug Class Stats')
    
    # Foglio 3: Conteggi incrociati
    cross_counts.to_excel(writer, sheet_name='Cross Counts')
    
    # Foglio 4: Percentuali incrociate
    cross_percentages.to_excel(writer, sheet_name='Cross Percentages')

print("\nResults saved to 'drug_statistics.xlsx'")