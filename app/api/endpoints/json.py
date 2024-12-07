import json5
from fastapi import APIRouter, HTTPException

from app.api.singeltons import openai_fetcher
from app.core.ai.prompts import get_fix_json_prompt
from app.schemas.json import FixedJsonOpenAiResponse, FixedJsonResponse, FixedJsonRequest

router = APIRouter()


@router.post("/fix", response_model=FixedJsonResponse)
async def fix_json(malformed_json_request: FixedJsonRequest):
    max_json_length = 512
    malformed_json = malformed_json_request.malformed_json
    try:
        # Try parsing the provided malformed JSON using json5
        parsed_json = json5.loads(str(malformed_json))
        return FixedJsonResponse(json=parsed_json, explanation='')
    except Exception as e:
        # Try fixing it with OpenAi
        if len(malformed_json) > max_json_length:
            raise HTTPException(status_code=422, detail="AI fixing only supported for json <= 512 chars")
        try:
            # Fetch the potential fixed JSON from OpenAI
            potential_fixed_json = await openai_fetcher.get_json_output(
                messages=get_fix_json_prompt(malformed_json, malformed_json_request.language),
                response_format=FixedJsonOpenAiResponse)
            fixed_json = potential_fixed_json.fixed_json
            explanation = potential_fixed_json.explanation

            # Try to parse the fixed JSON
            parsed_json = json5.loads(fixed_json)
            return FixedJsonResponse(json=parsed_json, explanation=explanation)
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to fix malformed JSON")
