"""Module for Statement Verifiers."""
from abc import ABC, abstractmethod
from enum import Enum

import torch
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)

from app.core.factVerification.models.claim_verification_model import ClaimVerificationModel


class Fact(Enum):
    """Represents the types a fact can have."""

    SUPPORTED = 0
    NOT_SUPPORTED = 1
    NOT_ENOUGH_INFO = 2
    SUPPORTS = 0
    REFUTES = 1

    def to_factuality(self) -> int:
        """Convert itself to a measurement."""
        factuality = {
            Fact.SUPPORTED: 1,
            Fact.NOT_SUPPORTED: 0,
            Fact.SUPPORTS: 1,
            Fact.REFUTES: 0,
            Fact.NOT_ENOUGH_INFO: 0
        }
        return factuality[self]


class StatementVerifier(ABC):
    """Abstract base class for verifying statements against evidence."""

    def __call__(self, statements: list[dict], evidence_batch: list[list[dict]]):
        """
        Verify a batch of statements against a batch of evidences.

        :param statements: list of statements to be verified.
        :param evidence_batch: list of evidences corresponding to the statements.
        :return: list of verification results.
        """
        return self.verify_statement_batch(statements, evidence_batch)

    @abstractmethod
    def set_premise_sent_order(self, sent_order: str):
        """
        Set the order in which premise sentences should be processed during verification.

        :param sent_order: The sentence order strategy ('reverse', 'top_last', or 'keep').
        """

    @abstractmethod
    def verify_statement(self, statement: dict, evidence: list[dict]):
        """
        Verify a single statement against a single evidence.

        :param statement: The statement to be verified.
        :param evidence: The evidence to verify the statement against.
        :return: Verification result.
        """

    @abstractmethod
    def verify_statement_batch(self,
                               statements: list[dict], evids_batch: list[list[dict]]) -> list[dict]:
        """
        Verify a batch of statements against a batch of evidences.

        :param statements: list of statements to be verified.
        :param evids_batch: list of evidences corresponding to the statements.
        :return: list of verification results.
        """


class ModelStatementVerifier(StatementVerifier):
    """
    StatementVerifier implementation that uses a machine learning model for verification.
    """

    MODEL_NAME = 'lukasellinger/claim-verification-model-top_last'

    def __init__(self, model_name: str = '', premise_sent_order: str = 'top_last'):
        self.model_name = model_name or self.MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = None
        self.premise_sent_order = None
        self.set_premise_sent_order(premise_sent_order)

    def set_premise_sent_order(self, sent_order: str):
        if sent_order not in {'reverse', 'top_last', 'keep'}:
            raise ValueError(
                "premise_sent_order needs to be either 'reverse', 'top_last', or 'keep'")
        self.premise_sent_order = sent_order

    def load_model(self):
        """Load the machine learning model for verification, if not already loaded."""
        if self.model is None:
            model_raw = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model = ClaimVerificationModel(model_raw).to(self.device)
            self.model.eval()

    def unload_model(self):
        """Unload the machine learning model and free up GPU resources."""
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache()
            self.model = None

    def verify_statement(self, statement: dict, evidence: list[dict]):
        return self.verify_statement_batch([statement], [evidence])[0]

    def _order_hypothesis(self, hypo_sents: list[str]):
        if self.premise_sent_order not in {'reverse', 'top_last', 'keep'}:
            raise ValueError(
                "premise_sent_order needs to be either 'reverse', 'top_last', or 'keep'")

        if not hypo_sents:
            return ''

        if self.premise_sent_order == 'reverse':
            ordered_sents = hypo_sents[::-1]
        elif self.premise_sent_order == 'top_last':
            ordered_sents = hypo_sents[1:] + [hypo_sents[0]]
        else:  # 'keep'
            ordered_sents = hypo_sents

        return ' '.join(ordered_sents)

    def verify_statement_batch(self,
                               statements: list[dict], evids_batch: list[list[dict]]) -> list[dict]:
        if not self.model:
            self.load_model()

        hypothesis_batch = [self._order_hypothesis([sentence['text'] for sentence in entry]) for
                            entry in evids_batch]
        predictions_batch = []
        for statement, hypothesis in zip(statements, hypothesis_batch):
            facts = statement.get('splits', [statement.get('text')])
            if not hypothesis:
                predictions = [Fact.NOT_SUPPORTED.name] * len(facts)
                factuality = Fact.NOT_SUPPORTED.to_factuality()
            else:
                model_inputs = self.tokenizer([hypothesis] * len(facts), facts,
                                              return_tensors='pt', padding=True).to(self.device)
                del model_inputs['token_type_ids']
                with torch.no_grad():
                    outputs = self.model(**model_inputs)
                    logits = outputs['logits']
                    probabilities = torch.softmax(logits, dim=-1)
                    predictions = torch.argmax(probabilities, dim=-1).tolist()

                factuality = sum(pred == 0 for pred in predictions) / len(predictions)
                predictions = [Fact.SUPPORTED.name if pred == 0 else Fact.NOT_SUPPORTED.name for
                               pred in predictions]
            factualities = [{'atom': fact, 'predicted': prediction} for fact, prediction in
                            zip(facts, predictions)]

            predictions_batch.append({
                'predicted': Fact.SUPPORTED.name if factuality == 1 else Fact.NOT_SUPPORTED.name,
                'factuality': factuality,
                'atoms': factualities
            })
        return predictions_batch


if __name__ == "__main__":
    verifier = ModelStatementVerifier(premise_sent_order='top_last')
    results = verifier.verify_statement_batch(
        [{'text': 'Sun is hot.'}, {'text': 'Sun is cold.'}],
        [[{'text': 'Sun is very very very hot.'}],
         [{'text': 'Sun is very very very hot.'}]]
    )
    print(results)