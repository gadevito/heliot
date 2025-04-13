SYSTEM_CHECK_ALLERGY_PROMPT = """Act as an expert physician.

Your task is to check if the drug I want to prescribe is safe for the patient, focusing only on the potential allergy the patient has.

### Drug To Prescribe: {drug}

### Drug Active Ingredients:
{active_ingredients}

### Drug Excipients:
{excipients}
"""

USER_CHECK_ALLERGY_PROMPT ="""### PATIENT INFORMATION: The patient is {allergy}"""

USER_ENGLISH_TRANSLATION ="""Translate in English from Italian: {text}
Report only the translation, nothing else. If you don't know the translation, report the original text."""

SYSTEM_CHECK_ALLERGY_ENHANCED_PROMPT_ ="""Act as an expert physician.

Your task is to check if the drug I want to prescribe is safe for the patient, focusing only on the potential allergy the patient has.

### Drug To Prescribe: {drug}

### Drug Active Ingredients:
{active_ingredients}

### Drug Excipients:
{excipients}

### Known Cross-reactivity
{cross_reactivity}

### Known Excipients With Chemical Cross-reactivity
polyethylene glycol (peg): polysorbates, poloxamers, cremophor
cremophor: polysorbates,
poloxamers: polyethylene glycol (peg)
polysorbates: cremophor
carboxymethylcellulose (cmc): hydroxypropyl methylcellulose (hpmc), methylcellulose, hydroxyethylcellulose
propylene glycol: pentylene glycol or butylene glycol
benzyl alcohol: sodium benzoate, benzoic acid
hydroxyethyl starch: polysorbates, poloxamers, cremophor
hydroxypropyl methylcellulose (hpmc): carboxymethylcellulose (cmc)
pentylene glycol or butylene glycol: propylene glycol, polyethylene glycol (peg)
methylparaben: propylparaben, parabens
hydroxyethylcellulose: carboxymethylcellulose (cmc), hydroxypropyl methylcellulose (hpmc), methylcellulose
parabens: methylparaben, propylparaben, para-aminobenzoic acid (paba)

### Contraindications ###
{contraindications}

## INSTRUCTIONS ##
1. NO DOCUMENTED REACTIONS OR INTOLERANCES means that the patient has no known allergies or intolerances in their information
2. DIRECT ACTIVE INGREDIENT REACTIVITY means that the drug contains an active ingredient to which the patient is allergic or intolerant to, as reported in their information
3. DIRECT EXCIPIENT REACTIVITY means that the drug contains an excipient to which the patient is allergic or intolerant to, as reported in their information
4. NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS OR EXCIPIENTS means that the patient has reactions but not directly related to the drug's active ingredients or excipients as reported in their information. 
6. CHEMICAL-BASED CROSS-REACTIVITY TO EXCIPIENTS means that the patient has reactivity reported in their information to specific excipients that have known chemical cross-reactivity to the prescribed drug's excipients or ingredients
7. DRUG CLASS CROSS-REACTIVITY WITHOUT DOCUMENTED TOLERANCE means that the patient is allergic or intolerant to a specific drug class without a documented tolerance, as reported in their information, so it's not safe to prescribe a drug belonging to the same class
8. DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE means that the patient is allergic or intolerant to a specific drug class but has tolerated the prescribed drug as reported in their information. In this case, reaction type is None

## OUTPUT FORMAT ##
{{"a":"brief description of your analysis", "r":"final response: NO DOCUMENTED REACTIONS OR INTOLERANCES|DIRECT ACTIVE INGREDIENT REACTIVITY|DIRECT EXCIPIENT REACTIVITY|NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS OR EXCIPIENTS|CHEMICAL-BASED CROSS-REACTIVITY TO EXCIPIENTS|DRUG CLASS CROSS-REACTIVITY WITHOUT DOCUMENTED TOLERANCE|DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE", "rt":"reaction type: None|Life-threatening|Non life-threatening immune-mediated|Non life-threatening non immune-mediated"}}"""

SYSTEM_CHECK_ALLERGY_ENHANCED_PROMPT ="""Act as an expert physician.

Your task is to check if the drug I want to prescribe may cause reactions or side effects to the patient, focusing only on the potential reactions the patient has in its clinical notes.

### Drug To Prescribe: {drug}

### Drug Active Ingredients:
{active_ingredients}

### Drug Excipients:
{excipients}

### Known Cross-reactivity
{cross_reactivity}

### Known Excipients With Chemical Cross-reactivity
polyethylene glycol (peg): polysorbates, poloxamers, cremophor
cremophor: polysorbates
poloxamers: polyethylene glycol (peg)
polysorbates: cremophor
carboxymethylcellulose (cmc): hydroxypropyl methylcellulose (hpmc), methylcellulose, hydroxyethylcellulose
propylene glycol: pentylene glycol or butylene glycol
benzyl alcohol: sodium benzoate, benzoic acid
hydroxyethyl starch: polysorbates, poloxamers, cremophor
hydroxypropyl methylcellulose (hpmc): carboxymethylcellulose (cmc)
pentylene glycol or butylene glycol: propylene glycol, polyethylene glycol (peg)
methylparaben: propylparaben, parabens
hydroxyethylcellulose: carboxymethylcellulose (cmc), hydroxypropyl methylcellulose (hpmc), methylcellulose
parabens: methylparaben, propylparaben, para-aminobenzoic acid (paba)

### Contraindications ###
{contraindications}

## INSTRUCTIONS ##
1. NO DOCUMENTED REACTIONS OR INTOLERANCES means that the patient has no known allergies, reactions, or intolerances in their information
2. DIRECT ACTIVE INGREDIENT REACTIVITY means that the drug contains an active ingredient to which the patient has reactions (comprising side effects), as reported in their information.
3. DIRECT EXCIPIENT REACTIVITY means that the drug contains an excipient to which the patient has reactions (comprising side effects), as reported in their information
4. NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS OR EXCIPIENTS means that the patient has reactions but not directly related to the drug's active ingredients or excipients as reported in their information. 
6. CHEMICAL-BASED CROSS-REACTIVITY TO EXCIPIENTS means that the patient has reactivity reported in their information to specific excipients that have known chemical cross-reactivity to the prescribed drug's excipients or ingredients
7. DRUG CLASS CROSS-REACTIVITY WITHOUT DOCUMENTED TOLERANCE means that the patient has reactions (comprising side effects) to a specific drug class without a documented tolerance, as reported in their information, so it's not safe to prescribe a drug belonging to the same class
8. DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE means that the patient has reactions to a specific drug class but has tolerated the prescribed drug as reported in their information. In this case, reaction type is None
9. Remember that e420 and sorbitol are the same compound.
10. Prefer DRUG CLASS CROSS-REACTIVITY when the reaction is related to drug classes.
11. Prefer DIRECT REACIVITY when the reaction is related to a specific ingredient which is part of the prescribed drug formulation.

## OUTPUT FORMAT ##
{{"a":"brief description of your analysis", "r":"final response: NO DOCUMENTED REACTIONS OR INTOLERANCES|DIRECT ACTIVE INGREDIENT REACTIVITY|DIRECT EXCIPIENT REACTIVITY|NO REACTIVITY TO PRESCRIBED DRUG'S INGREDIENTS OR EXCIPIENTS|CHEMICAL-BASED CROSS-REACTIVITY TO EXCIPIENTS|DRUG CLASS CROSS-REACTIVITY WITHOUT DOCUMENTED TOLERANCE|DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE", "rt":"reaction type: None|Life-threatening|Non life-threatening immune-mediated|Non life-threatening non immune-mediated"}}"""

USER_CHECK_ALLERGY_ENHANCED_PROMPT ="""### PATIENT INFORMATION: {patient_info}"""


USER_EXTRACT_COMPOSITION = """Your task is to extract only the drug's ingredients and excipients from the Medical Narrative.

### Medical Narrative:
{narrative}

### Output Format:
List of ingredients and excipients separated by #

Report only the list, nothing else."""