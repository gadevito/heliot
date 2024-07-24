from pydantic import BaseModel

class AllergyCheckRequest(BaseModel):
    drug_code: str
    allergy: str
    