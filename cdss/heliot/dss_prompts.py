SYSTEM_CHECK_ALLERGY_PROMPT = """Act as an expert physician.

Your task is to check if the drug I want to prescribe is safe for the patient, focusing only on the potential allergy the patient has.

### Drug To Prescribe: {drug}

### Drug Active Ingredients:
{active_ingredients}

### Drug Excipients:
{excipients}
"""

USER_CHECK_ALLERGY_PROMPT ="""### PATIENT INFORMATION: The patient is {allergy}"""