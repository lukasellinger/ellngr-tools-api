"""Simple pipeline run script."""
from app.core.factVerification.pipeline_modules.evidence_fetcher import WikipediaEvidenceFetcher
from app.core.factVerification.pipeline_modules.evidence_selector import ModelEvidenceSelector
from app.core.factVerification.pipeline_modules.sentence_connector import ColonSentenceConnector
from app.core.factVerification.pipeline_modules.statement_verifier import ModelStatementVerifier
from app.core.factVerification.pipeline_modules.translator import OpusMTTranslator
from app.core.factVerification.pipelines.definition_pipeline import Pipeline

evid_selector = ModelEvidenceSelector(evidence_selection='mmr')
stm_verifier = ModelStatementVerifier(
    model_name='MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7')

pipeline = Pipeline(translator=OpusMTTranslator(),
                    sent_connector=ColonSentenceConnector(),
                    claim_splitter=None,
                    evid_fetcher=WikipediaEvidenceFetcher(),
                    evid_selector=evid_selector,
                    stm_verifier=stm_verifier,
                    lang='en')
print(pipeline.verify(word='unicorn',
                claim='mythical horse with a single horn'))
