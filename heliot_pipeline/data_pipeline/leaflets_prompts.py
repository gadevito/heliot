USER_ENGLISH_TRANSLATION ="""Translate in English from Italian: {text}
Report only the translation, nothing else. If you don't know the translation, report the original text."""

USER_PROCESS_ACTIVE_INGREDIENTS ="""Your task is to extract only the drug's active ingredients, given its name and pharmaceutical form.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Composition:
{composition}

### Output Format:
List of active ingredients separated by #

Report only the list, nothing else."""

USER_PROCESS_INACTIVE_INGREDIENTS="""Your task is to extract only the drug's inactive ingredients (excipients), given its name and pharmaceutical form.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Composition:
{composition}

### Output Format:
List of inactive ingredients separated by #

**Important:**
Focus only on the exact pharmaceutical form of the drug to extract its composition.

Report only the list, nothing else."""

USER_PROCESS_POSOLOGY = """Your task is to extract the posology only for the drug name and its pharmaceutical form I'll provide below.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Posology:
{posology}

### Instructions:
- Report only the posology specifically related to the drug name and its pharmaceutical form I provided. 
- You must not report information related to different pharmaceutical forms of the provided drug.
- Do not elaborate or summarize the text, it must be the same extracted from the provided "Posology".
- If the posology text mentions other pharmaceutical forms for the provided drug, exclude those parts and report only the relevant information.
- **Important:** If the posology text includes any mention of alternative pharmaceutical forms of the provided drug, you must exclude those parts and only report the posology related to the provided drug name and its specified pharmaceutical form.
- **Reminder:** Carefully review the text for any mentions of alternative pharmaceutical forms for the provided drug and explicitly exclude those parts.

### Output format:
If the  "Posology" text is fully related to the specific drug name and its pharmaceutical form I provided and does not mention information related to different pharmaceutical forms of the provided drug, simply answer "<<ALL>>", otherwise report only the posology related to the drug name and its pharmaceutical form I provided."""


USER_PROCESS_CONTRAINDICATIONS ="""Your task is to extract the contraindications only for the drug name and its pharmaceutical form I'll provide below.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Contraindications:
{indications}

### Instructions:
- Report only the contraindications specifically related to the drug name and its pharmaceutical form I provided. 
- You must not report information related to different pharmaceutical forms of the provided drug.
- Do not elaborate or summarize the text, it must be the same extracted from the provided "Contraindications".
- If the Contraindications text mentions other pharmaceutical forms for the provided drug, exclude those parts and report only the relevant information.
- **Important:** If the Contraindications text includes any mention of alternative pharmaceutical forms of the provided drug, you must exclude those parts and only report the contraindications related to the provided drug name and its specified pharmaceutical form.
- **Reminder:** Carefully review the text for any mentions of alternative pharmaceutical forms for the provided drug and explicitly exclude those parts.

### Output format:
If the  "Contraindications" text is fully related to the specific drug name and its pharmaceutical form I provided and does not mention information related to different pharmaceutical forms of the provided drug, simply answer "<<ALL>>", otherwise report only the contraindications related to the drug name and its pharmaceutical form I provided."""


USER_PROCESS_INCOMPATIBILITIES = """Your task is to extract the drug incompatibilities only for the drug name and its pharmaceutical form I'll provide below.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Drug incompatibilities:
{incompatibilities}

### Instructions:
- Report only the incompatibilities specifically related to the drug name and its pharmaceutical form I provided. 
- You must not report information related to different pharmaceutical forms of the provided drug.
- Do not elaborate or summarize the text, it must be the same extracted from the provided "Drug incompatibilities".
- If the "Drug incompatibilities" text mentions other pharmaceutical forms for the provided drug, exclude those parts and report only the relevant information.
- **Important:** If the "Drug incompatibilities" text includes any mention of alternative pharmaceutical forms of the provided drug, you must exclude those parts and only report the incompatibilities related to the provided drug name and its specified pharmaceutical form.
- **Reminder:** Carefully review the text for any mentions of alternative pharmaceutical forms for the provided drug and explicitly exclude those parts.

### Output format:
If the  "Drug incompatibilities" text is fully related to the specific drug name and its pharmaceutical form I provided and does not mention information related to different pharmaceutical forms of the provided drug, simply answer "<<ALL>>", otherwise report only the incompatibilities related to the drug name and its pharmaceutical form I provided."""


USER_PROCESS_INTERACTIONS = """Your task is to extract the drug interactions only for the drug name and its pharmaceutical form I'll provide below.

### Drug: {drug_name}
### Pharmaceutical form: {drug_form}

### Drug interactions:
{interactions}

### Instructions:
- Report only the interactions specifically related to the drug name and its pharmaceutical form I provided. 
- You must not report information related to different pharmaceutical forms of the provided drug.
- Do not elaborate or summarize the text, it must be the same extracted from the provided "Drug interactions".
- If the "Drug interactions" text mentions other pharmaceutical forms for the provided drug, exclude those parts and report only the relevant information.
- **Important:** If the "Drug interactions" text includes any mention of alternative pharmaceutical forms of the provided drug, you must exclude those parts and only report the interactions related to the provided drug name and its specified pharmaceutical form.
- **Reminder:** Carefully review the text for any mentions of alternative pharmaceutical forms for the provided drug and explicitly exclude those parts.

### Output format:
If the  "Drug interactions" text is fully related to the specific drug name and its pharmaceutical form I provided and does not mention information related to different pharmaceutical forms of the provided drug, simply answer "<<ALL>>", otherwise report only the interactions related to the drug name and its pharmaceutical form I provided."""

USER_PROCESS_CROSS_REACTIONS = """In the following text, I need to know the active ingredients that cause cross-reactivity for the following drug with other drugs.

## DRUG INFO ##
Drug: {drug_name}
Active Ingredients of the drug: {active_ingredients}

## TEXT ##
{text}

## Instructions ##
1. **Thorough Analysis:** Carefully read and analyze the entire text provided. Pay special attention to any sections discussing allergies, hypersensitivity, cross-reactivity, and other drug interactions.

2. **Focus on Cross-Reactivity and Allergies:** Identify only explicit mentions of allergic cross-reactivity or hypersensitivity that involve the active ingredient(s) of the specified drug and other drugs. This includes direct statements about cross-reactivity due to allergies, as well as any implications or warnings related to it. Distinguish between allergic reactions and other types of interactions or adverse effects.

3. **Highlight Specific Drugs:** Specifically look for mentions of other drugs that may cause cross-reactivity with the active ingredient(s) of the given drug due to allergies. Ensure that these are drugs not listed as active ingredients in the given drug.

4. **Exact Drug Names:** All drug names must be reported exactly as they appear within the text. Singularize names where necessary and maintain consistency with the text.

5. **Assess and Report:** If the text provides information on cross-reactivity caused by allergies with other drugs, report it in the specified JSON format. If the text discusses other types of interactions or adverse effects without mentioning allergies, note this distinction. If no such information is present, return an empty JSON.

## Output Format ##
JSON:
```json
{{
  "description": "Provide a concise overview (1-2 paragraphs) of clinical/theoretical evidence supporting the possibility of cross-sensitivity between drugs due to allergies. Include any warnings or alerts relevant to this issue. If the text discusses other interactions or adverse effects, do not report it.", 
  "incidence": "State the reported cross-sensitivity rate due to allergies. Use values like: At least X%|Up to X%|X%|X-Y%|Common|Uncommon|Rare|Single case reports|Theoretical. If not allergy-related, specify 'Not applicable'.", 
  "da": "Specify the drug active ingredient causing cross-reactivity due to allergies", 
  "cross_sensitive_drugs": [{{"ai": "List all potential active ingredients from other drugs that cause cross-reaction due to allergies. Names must be reported exactly as they appear in the text. Singularized."}}]
}}
```

**Important:** 
- Use singular forms where applicable.
- Description must start be reported as an alert, but do not start it with "Alert:".
- Ensure accuracy in reporting drug names as they appear in the text.
- The text must explicit contain known cross-reactive drugs. For example, Beta-lactams, Antibiotic sulfonamides, Proton pump inhibitors, Opioids, ASA and nonsteroidal anti-inflammatory drugs, neuromuscular blocking agents, Radiocontrast media, etc.
- Focus on explicit drug cross-reactivity due to allergies with drugs not listed as active ingredients in the given drug. If no such explicit information is found, report an empty JSON.

Answer only with the JSON:"""