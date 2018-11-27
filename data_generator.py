""" Uses the scripts contained within explorer.py to generate training and test data."""

import pandas as pd
import numpy as np
from knowledgestore import ks
import explorer
from multiprocessing import Pool
import copy
from logging import log

all_article_uris = explorer.all_article_uris
QUESTION_SIGN = "?"


def generate_all_data():
    all_data = pd.DataFrame()
    with open("data.csv", "w+") as file:
        for uri in all_article_uris["article"]:  # Todo: Parralize
            next_data = generate_data_from_uri(uri)
            if not len(next_data) == 0:
                all_data = all_data.append(next_data, ignore_index=True)

                all_data.to_csv(file)
				


def generate_data_from_uri(uri):
    answers = explorer.get_triplets(uri)
    if len(answers) == 0:
        return []
    questions = np.array(answers)
    questions[:, 1] = QUESTION_SIGN
    result = pd.DataFrame()
    for QAPair in range(len(answers)):
        result = result.append(
            {"answer": answers[QAPair], "question": questions[QAPair], "text": ks.run_files_query(uri), "Article": uri},
            ignore_index=True)
    return result


def generate_classification_data(agent, patient, chars, raw_text):
    correct_relations = [raw_text[c[0], c[1]] for c in chars]
    splits_at = get_positions_of_char_in_text(" ", raw_text)
    splits_at.insert(0, 0)
    splits_at.insert(-1, len(raw_text))
    words_by_position = [(splits_at[x], splits_at[x + 1]) for x in range(len(splits_at) - 1)]

    result_frame = pd.DataFrame()
    for word_by_position in words_by_position:
        classification = word_by_position in correct_relations
        pandas_line = pd.DataFrame({"agent": agent, "patient": patient, "word_by_char": word_by_position,
                                    "classification": classification, "raw_text": raw_text})
        result_frame = result_frame.append(pandas_line, ignore_index=True)
    return result_frame


def get_positions_of_char_in_text(sought_char, text):
    return [pos for pos, char in enumerate(text) if char == sought_char]


if __name__ == "__main__":
    generate_triples_from_uri("http://en.wikinews.org/wiki/Invisibility_shield_gets_blueprint")
