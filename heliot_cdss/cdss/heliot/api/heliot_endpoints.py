from .models.heliot_models import *
from .services.heliot_llm import *
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import os
from openai import OpenAI

router = APIRouter()


heliot = HeliotLLM()


@router.post("/allergy_check")
async def allergy_check(request: AllergyCheckRequest):
    drug_code = request.drug_code
    allergy = request.allergy

    return StreamingResponse(heliot.dss_check(drug_code, allergy), media_type='text/event-stream')