import asyncio
from app.core.factVerification.pipeline_modules.claim_splitter import DisSimSplitter
from app.core.factVerification.pipeline_modules.evidence_fetcher import WikipediaEvidenceFetcher
from app.core.factVerification.pipeline_modules.evidence_selector import ModelEvidenceSelector
from app.core.factVerification.pipeline_modules.statement_verifier import ModelSplitStatementVerifier
from app.core.factVerification.pipeline_modules.translator import OpusMTTranslator
from app.core.factVerification.pipelines.fact_pipeline import ProgressPipeline

# Initialize pipeline components
evid_selector = ModelEvidenceSelector(evidence_selection='mmr')
stm_verifier = ModelSplitStatementVerifier(
    model_name='MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7'
)

pipeline = ProgressPipeline(
    translator=OpusMTTranslator(),
    claim_splitter=DisSimSplitter(),
    evid_fetcher=WikipediaEvidenceFetcher(),
    evid_selector=evid_selector,
    stm_verifier=stm_verifier,
    lang='de'
)


async def main():
    # Run the pipeline and verify the claim
    result = await pipeline.verify('Eine Hose ist ein Kopf und ist lustig')
    print(result)


# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
