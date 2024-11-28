from fastapi import APIRouter

from app.api.singeltons import openai_fetcher
from app.core.ai.prompts import get_factsplit_prompt, get_summary_prompt
from app.schemas.text import (
    FactsplitResponse,
    FactsplitRequest,
    FactsplitOpenAiResponse,
    SummaryRequest,
    SummaryResponse,
    SummaryOpenAiResponse)

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(summary_request: SummaryRequest):
    ai_response = await openai_fetcher.get_json_output(
        messages=get_summary_prompt(summary_request.text, summary_request.language),
        response_format=SummaryOpenAiResponse)

    return SummaryResponse(summary=ai_response.summary)


@router.post("/fact-split", response_model=FactsplitResponse)
async def sentence_fact_split(factsplit_request: FactsplitRequest):
    sentence = factsplit_request.sentence
    ai_response = await openai_fetcher.get_json_output(
        messages=get_factsplit_prompt(sentence,
                                      factsplit_request.language),
        response_format=FactsplitOpenAiResponse)

    return FactsplitResponse(original_sentence=sentence,
                             facts=ai_response.facts)
