USER_ENGLISH_TRANSLATION ="""Translate in English: {text}
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