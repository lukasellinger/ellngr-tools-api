"""Module for claim splitters."""
from abc import ABC, abstractmethod

from app.core.factVerification.general_utils.utils import sentence_simplification


class ClaimSplitter(ABC):
    """
    Abstract base class for claim splitters.

    Defines the interface for claim splitting, providing methods for both
    single text and batch processing of atomic claims.
    """

    def __call__(self, batch):
        return self.get_atomic_claims_batch(batch)

    @abstractmethod
    def get_atomic_claims(self, text: str) -> dict:
        """
        Obtain atomic claims from a single text.

        :param text: The input text to split into atomic claims.
        :return: A list of atomic claims.
        """

    @abstractmethod
    def get_atomic_claims_batch(self, texts: list[str]) -> list[dict]:
        """
        Obtain atomic claims from a batch of texts.

        :param texts: List of texts to split into atomic claims.
        :return: A list of lists, where each list contains atomic claims for a given text.
        """


class DisSimSplitter(ClaimSplitter):
    """DisSim Claim Splitter https://github.com/Lambda-3/DiscourseSimplification"""
    def get_atomic_claims(self, text: str) -> dict:
        output = sentence_simplification([text])
        return output[0]

    def get_atomic_claims_batch(self, texts: list[str]) -> list[dict]:
        return sentence_simplification(texts)


if __name__ == "__main__":
    splitter = DisSimSplitter()
    print(splitter.get_atomic_claims_batch([
        "Alice likes soccer and Bob likes tennis."
    ]))
