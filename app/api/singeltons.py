from app.core.ai.openai_fetcher import OpenAiFetcher
from app.core.factVerification.pipeline_modules.evidence_fetcher import WikipediaEvidenceFetcher
from app.core.factVerification.pipeline_modules.evidence_selector import ModelEvidenceSelector
from app.core.factVerification.pipeline_modules.sentence_connector import ColonSentenceConnector
from app.core.factVerification.pipeline_modules.statement_verifier import ModelStatementVerifier
from app.core.factVerification.pipeline_modules.translator import OpusMTTranslator
from app.core.factVerification.pipelines.definition_pipeline import ProgressPipeline

openai_fetcher = OpenAiFetcher()

evid_selector = ModelEvidenceSelector()
evid_selector.load_model()
stm_verifier = ModelStatementVerifier()
stm_verifier.load_model()

# Initialize the pipeline instance
pipeline = ProgressPipeline(
    OpusMTTranslator(),
    ColonSentenceConnector(),
    None,
    WikipediaEvidenceFetcher(),
    evid_selector,
    stm_verifier,
    'de'
)