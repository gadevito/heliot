from ...db_management import *
from ...ingredients_onthology import *
from ...dss_prompts import *
from ...leaflets_prompts import *
import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import traceback
import json
from typing import AsyncGenerator

class HeliotLLM:
    def __init__(self, db_uri="drugs_db", synonym_csv="ingredients_synonyms.csv"):
        self.dbm = DatabaseManagement(store_lower_case=True)
        self.ont = SynonymManager(synonym_csv)
        # Initialize the OPENAI API
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    # Translate the text in English
    def _translate_in_english(self, text) -> str:
        try:
            response = self.client.chat.completions.create(model="gpt-4o",
                                    messages=[{"role": "system", "content": ""},
                                            {"role": "user", "content":  USER_ENGLISH_TRANSLATION.format(text=text)}],
                                    max_tokens=3000,
                                    temperature = 0)
            cleaned_text = response.choices[0].message.content
            return cleaned_text
        except Exception as e:
            print(f"Failed to process text with GPT-4: {e}")
            return None

    def _internal_search_drug(self,drug_code:str):
        print("SEARCHING...", drug_code)
        return self.dbm.search_drug(drug_code)


    def _chat_completion_create(self, model, messages, max_tokens, temperature, stream):
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )
        for event in stream:
                if event.choices[0].delta.content is not None:
                    print(event.choices[0].delta.content, end="")
                    # yield "data: " + event.choices[0].delta.content + "\n\n"
                    yield f"data: {json.dumps({'message': event.choices[0].delta.content})}\n\n"



    def dss_check(self, drug_code: str, allergy: str):
        print("DRUG CODE", drug_code)
        
        if len(allergy) >0:
            allergy = allergy.lower()
            with ThreadPoolExecutor() as executor:
                future_drug = executor.submit(self._internal_search_drug, drug_code)
                future_translation = executor.submit(self._translate_in_english, allergy)
                    
                # Wait for the results
                drg = future_drug.result()
                allergy = future_translation.result()
                al = self.ont.find_standard_name(allergy)
                allergy_type = "allergic to "+al
        else:
            allergy_type = "not allergic"
            drg = self.dbm.search_drug(drug_code)

        composition = drg['composition']
        excipients = drg['excipients']
        prescription = drg['drug_name']

        try:
            response = self.client.chat.completions.create(model="gpt-4o",
                                    messages=[{"role": "system", "content": SYSTEM_CHECK_ALLERGY_PROMPT.format(drug=prescription, active_ingredients=composition, excipients=excipients)},
                                            {"role": "user", "content":  USER_CHECK_ALLERGY_PROMPT.format( allergy=allergy_type)}],
                                    max_tokens=3000,
                                    temperature = 0,
                                    stream=True,
                                    stream_options= {"include_usage": True})
            for event in response:
                if event.choices is not None and len(event.choices)>0 and event.choices[0].delta.content is not None:
                    #yield event.choices[0].delta.content+"\n"
                    yield f"data: {json.dumps({'message': event.choices[0].delta.content})}\n\n"
                if hasattr(event, 'usage') and event.usage is not None:
                    print(event.usage)
                    prompt_tokens = event.usage.prompt_tokens
                    completion_tokens = event.usage.completion_tokens
                    total_tokens = event.usage.total_tokens
                    yield f"data: {json.dumps({'input': prompt_tokens, 'output': completion_tokens, 'total':  total_tokens})}\n\n"
        except Exception as e:
            stack_trace = traceback.format_exc()
            
            # Ora puoi stampare, loggare o manipolare la stringa come preferisci
            print("Si è verificata un'eccezione:")
            print(stack_trace)
            yield None

