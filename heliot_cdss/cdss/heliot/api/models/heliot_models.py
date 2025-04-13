from pydantic import BaseModel

class AllergyCheckRequest(BaseModel):
    drug_code: str
    allergy: str


class AllergyCheckEnhancedRequest(BaseModel):
    patient_id: str 
    drug_code: str 
    clinical_notes: str
    store: bool = False