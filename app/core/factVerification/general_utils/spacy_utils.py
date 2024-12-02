"""General utils using spacy for processing."""

import spacy


nlp = spacy.load("en_core_web_lg")
german_nlp = spacy.load("de_core_news_lg")


def get_doc(txt: str, lang: str = 'en'):
    """
    Returns a spacy Doc object for a given text in the specified language.

    :param txt: The input text.
    :param lang: Language of the input text ('en' for English, 'de' for German).
    :return: A spacy Doc object.
    """
    if lang == 'en':
        return nlp(txt)
    if lang == 'de':
        return german_nlp(txt)
    raise ValueError(f'Language {lang} not supported.')


def get_main_entity(txt: str, lang: str = 'en'):
    doc = get_doc(txt, lang)

    if doc.ents:
        return doc.ents[0].text

    for token in doc:
        if token.dep_ in {"nsubj", "ROOT", "pobj", "dobj"} and token.pos_ == "NOUN":
            return token.text
    return None


def split_into_sentences(txt: str, lang: str = 'en') -> list[str]:
    """Split a text into sentences."""
    doc = get_doc(txt, lang)
    return [sent.text.strip() for sent in doc.sents]


def split_into_passage_sentences(text: str,
                                 sentence_limit: int = 3,
                                 lang: str = 'en') -> list[list[str]]:
    """
    Splits a text into passages, each containing a limited number of sentences.

    :param text: The input text.
    :param sentence_limit: Maximum number of sentences per passage.
    :param lang: Language of the text ('en' for English, 'de' for German).
    :return: A list of passages, each being a list of sentences.
    """
    sentences = split_into_sentences(text, lang)
    passages = []
    for i in range(0, len(sentences), sentence_limit):
        passages.append(sentences[i:i + sentence_limit])

    return passages
