import asyncio
from copy import deepcopy
from typing import Tuple

from app.core.factVerification.pipeline_modules.claim_splitter import ClaimSplitter
from app.core.factVerification.pipeline_modules.evidence_fetcher import EvidenceFetcher
from app.core.factVerification.pipeline_modules.evidence_selector import EvidenceSelector
from app.core.factVerification.pipeline_modules.sentence_connector import SentenceConnector
from app.core.factVerification.pipeline_modules.statement_verifier import StatementVerifier
from app.core.factVerification.pipeline_modules.translator import Translator


class Pipeline:
    """General Pipeline for fetching evidence, selecting evidence, and verifying claims."""

    def __init__(self,
                 translator: Translator | None,
                 sent_connector: SentenceConnector,
                 claim_splitter: ClaimSplitter | None,
                 evid_fetcher: EvidenceFetcher,
                 evid_selector: EvidenceSelector,
                 stm_verifier: StatementVerifier,
                 lang: str):
        self.translator = translator
        self.sent_connector = sent_connector
        self.claim_splitter = claim_splitter
        self.evid_fetcher = evid_fetcher
        self.evid_selector = evid_selector
        self.stm_verifier = stm_verifier
        self.lang = lang

    def verify_batch(self, batch: list[dict], only_intro: bool = True) -> list[dict]:
        """
        Verify a batch of claims by fetching, selecting, and verifying evidence.

        :param batch: list of dictionaries containing 'word' and 'text'.
        :param only_intro: Flag to indicate if only the introductory section of documents should
        be considered.
        :return: list of outputs with factuality and selected evidences.
        """
        processed_batch = deepcopy(batch)

        if self.lang != 'en':
            translation_batch = self.translator(processed_batch)
            evid_fetcher_input = [{**b, 'translated_word': t.get('word')} for b, t in
                                  zip(batch, translation_batch)]
        else:
            translation_batch = processed_batch
            evid_fetcher_input = [{**b, 'translated_word': b.get('word')} for b in batch]

        evid_words, evids = self.evid_fetcher(evid_fetcher_input, word_lang=self.lang,
                                              only_intro=only_intro)

        outputs = []
        filtered_batch = []
        filtered_evids = []
        filtered_translations = []
        for entry, evid, word, translation in zip(processed_batch, evids, evid_words,
                                                  translation_batch):
            if not evid:
                outputs.append(
                    {'word': entry.get('word'),
                     'claim': entry.get('text'),
                     'predicted': -1,
                     'in_wiki': 'No'})
            else:
                filtered_batch.append(entry)
                filtered_evids.append(evid)
                filtered_translations.append({**translation, 'word': word})

        if not filtered_batch:
            return outputs

        processed_batch = self.sent_connector(filtered_translations)

        if self.claim_splitter:
            processed_batch = self.claim_splitter([entry['text'] for entry in processed_batch])

        evids_batch = self.evid_selector(processed_batch, filtered_evids)
        factualities = self.stm_verifier(processed_batch, evids_batch)

        for factuality, evidence, entry in zip(factualities, evids_batch, filtered_batch):
            outputs.append({'word': entry.get('word'),
                            'claim': entry.get('text'),
                            **factuality,
                            'selected_evidences': evidence,
                            'in_wiki': 'Yes'})
        return outputs

    def verify(self, word: str, claim: str, only_intro: bool = True) -> dict:
        """
        Verify a single claim.

        :param word: The word to verify.
        :param claim: The claim to verify.
        :param only_intro: Flag to indicate if only the introductory section of documents should
        be considered.
        :return: Verification result.
        """
        entry = {'word': word, 'text': claim}
        return self.verify_batch([entry], only_intro=only_intro)[0]

    @staticmethod
    def filter_batch_for_wikipedia(batch: list[dict],
                                   evids_batch: list[list[dict]],
                                   outputs) -> Tuple[list[dict], list[list[dict]], list[dict]]:
        filtered_batch, filtered_evids = [], []
        for evid in evids_batch:
            evid[:] = [d for d in evid if d.get('title', '').endswith('(wikipedia)')]

        for entry, evid in zip(batch, evids_batch):
            if len(evid) > 0:
                filtered_batch.append(entry)
                filtered_evids.append(evid)
            else:
                outputs.append(
                    {'id': entry.get('id'),
                     'word': entry.get('word'),
                     'claim': entry.get('claim'),
                     'connected_claim': entry.get('connected_claim'),
                     'label': entry.get('label'),
                     'predicted': -1,
                     'in_wiki': 'No'
                     })

        return filtered_batch, filtered_evids, outputs

    def _prep_evidence_output(self, evidence: list[dict]) -> list[dict]:
        max_intro_sent_indices = self.evid_fetcher.get_max_intro_sent_idx()
        for entry in evidence:
            entry['in_intro'] = entry.get('line_idx') <= max_intro_sent_indices.get(
                entry.get('title'), -1)
        return evidence


class ProgressPipeline(Pipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    async def verify(self, word: str, claim: str, only_intro: bool = True):
        if self.progress_callback:
            await self.progress_callback("startingVerification")

        if self.translator and self.lang != 'en':
            if self.progress_callback:
                await self.progress_callback("translating")
            translated = await asyncio.to_thread(self.translator, [{'word': word, 'text': claim}])
            translated = translated[0]
            translated_word = translated.get('word', word)
            translated_claim = translated.get('text', claim)
        else:
            translated_word = word
            translated_claim = claim

        if self.progress_callback:
            await self.progress_callback("fetchingEvidence")
        evid_words, evids = self.evid_fetcher(
            [{'word': word, 'translated_word': translated_word}],
            word_lang=self.lang,
            only_intro=only_intro
        )

        if not evids or all(not sublist for sublist in evids):
            if self.progress_callback:
                await self.progress_callback("noEvidenceFound")
            return {'word': word, 'claim': claim, 'predicted': '', 'in_wiki': 'No'}

        if self.progress_callback:
            await self.progress_callback("processingClaim")
        processed_claim = await asyncio.to_thread(self.sent_connector, [
            {'word': evid_words[0], 'text': translated_claim}])
        processed_claim = processed_claim[0]

        if self.claim_splitter:
            if self.progress_callback:
                await self.progress_callback("splittingClaim")
            processed_claim = await asyncio.to_thread(self.claim_splitter,
                                                      [processed_claim['text']])
            processed_claim = processed_claim[0]

        if self.progress_callback:
            await self.progress_callback("selectingEvidence")
        selected_evids = await asyncio.to_thread(self.evid_selector, [processed_claim], evids)
        selected_evids = selected_evids[0]

        if self.progress_callback:
            await self.progress_callback("verifyingStatement")
        factuality = await asyncio.to_thread(self.stm_verifier, [processed_claim], [selected_evids])
        factuality = factuality[0]

        if self.progress_callback:
            await self.progress_callback("verificationComplete")

        return {
            'word': word,
            'claim': claim,
            **factuality,
            'selected_evidences': selected_evids,
            'in_wiki': 'Yes'
        }
