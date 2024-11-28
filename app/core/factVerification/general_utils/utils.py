import itertools
import subprocess

import numpy as np
from rank_bm25 import BM25Okapi

from app.core.utils.reader import JSONReader, LineReader
from config import PROJECT_DIR


def generate_case_combinations(txt: str) -> list[str]:
    """
    Generates all combinations of uppercase and lowercase for the first letter of each word in
    a string.

    :param txt: The input string.
    :return: A list of all case variations for the input text.
    """
    words = txt.split()
    combinations = []

    # Generate all combinations of upper and lower case for the first letter of each word
    for case_pattern in itertools.product(*[(word[0].lower(), word[0].upper()) for word in words]):
        # Reconstruct the sentence with the current case pattern
        combination = " ".join(
            pattern + word[1:] for pattern, word in zip(case_pattern, words)
        )
        combinations.append(combination)

    return combinations


def remove_duplicate_values(d: dict):
    """
    Removes duplicate values from a dictionary, keeping only the first occurrence of each value.

    :param d: The input dictionary.
    :return: A dictionary without duplicate values.
    """
    seen_values = set()
    unique_dict = {}

    for key, value in d.items():
        if isinstance(value, list):
            value_tuple = tuple(value)  # Convert list to tuple
        else:
            value_tuple = value  # Use the value directly if it's not a list

        if value_tuple not in seen_values:
            unique_dict[key] = value
            seen_values.add(value_tuple)
    return unique_dict


def split_into_passages(text: str | list[str], tokenizer, max_length=256) -> list[str]:
    """
    Splits text into passages of a specified token length using a tokenizer.

    :param text: The input text or list of texts.
    :param tokenizer: A tokenizer to tokenize the input text.
    :param max_length: The maximum length of each passage in tokens.
    :return: A list of text passages.
    """
    if isinstance(text, str):
        text = [text]
    passages = [[]]
    for sent in text:
        assert len(sent.strip()) > 0
        tokens = tokenizer(sent)["input_ids"]
        max_length = max_length - len(passages[-1])
        if len(tokens) <= max_length:
            passages[-1].extend(tokens)
        else:
            passages[-1].extend(tokens[:max_length])
            offset = max_length
            while offset < len(tokens):
                passages.append(tokens[offset:offset + max_length])
                offset += max_length

    psgs = [tokenizer.decode(tokens) for tokens in passages if
            np.sum([t not in [0, 2] for t in tokens]) > 0]
    return psgs


def rank_docs(query: str, docs: list[str], k=5, get_indices=True) -> list[str] | list[int]:
    """
    Get the top k most similar documents according to the query using the BM25 algorithms.
    :param query: query sentence.
    :param docs: documents to rank.
    :param k: amount of documents to return
    :param get_indices: If True, returns the indices, else the text.
    :return: List of most similar documents.
    """

    def preprocess(txt: str):
        """Lower the text."""
        return txt.lower()

    query = preprocess(query)
    docs = [preprocess(doc) for doc in docs]
    tokenized_corpus = [doc.split(" ") for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    if get_indices:
        scores = np.array(bm25.get_scores(query.split(" ")))
        return np.flip(np.argsort(scores)[-k:]).tolist()
    return bm25.get_top_n(query.split(" "), docs, k)


def sentence_simplification(sentences: list[str]) -> list[dict]:
    """
    Simplifies a list of sentences using the DiscourseSimplification repository.

    :param sentences: A list of sentences to simplify.
    :return: A list of dictionaries with original and simplified sentences.
    """
    discourse_simplification = PROJECT_DIR.joinpath('../DiscourseSimplification')
    LineReader().write(discourse_simplification.joinpath('input.txt'), sentences, mode='w')
    command = ["mvn", "-f", discourse_simplification.joinpath("pom.xml"), "clean", "compile",
               "exec:java"]
    subprocess.run(command, text=True, cwd=discourse_simplification, check=True)
    outputs = JSONReader().read(discourse_simplification.joinpath('output.json')).get('sentences')
    outputs = [{'text': entry.get('originalSentence'),
                'splits': [split.get('text') for split in entry.get('elementMap').values()]}
               for entry in outputs]
    return outputs

