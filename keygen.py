#!/usr/bin/env python3

import random

from keybert import KeyBERT

# doc = """
#     Supervised learning is the machine learning task of learning a function that
#     maps an input to an output based on example input-output pairs. It infers a
#     function from labeled training data consisting of a set of training examples.
#     In supervised learning, each example is a pair consisting of an input object
#     (typically a vector) and a desired output value (also called the supervisory signal).
#     A supervised learning algorithm analyzes the training data and produces an inferred function,
#     which can be used for mapping new examples. An optimal scenario will allow for the
#     algorithm to correctly determine the class labels for unseen instances. This requires
#     the learning algorithm to generalize from the training data to unseen situations in a
#     'reasonable' way (see inductive bias).
# """

# doc = """
# Search the lyrics of a song Search on Bing for the lyrics of your favorite song
# """

doc = "Let's watch that movie again! Earn 10 Rewards points searching on Bing for your favorite movies"

# doc = "Translate anything Search using Bing to translate any word you want"

# jeremy0330@book2020 ➜  Microsoft-Rewards-Farmer git:(service.20240627) ✗ ./foo.py
# [('bing', 0.5208), ('lyrics', 0.5063), ('search', 0.4434), ('song', 0.3799), ('favorite', 0.1905)]
# jeremy0330@book2020 ➜  Microsoft-Rewards-Farmer git:(service.20240627) ✗ ./foo.py
# [('bing', 0.4898), ('movie', 0.3836), ('movies', 0.3549), ('favorite', 0.2811), ('again', 0.229)]
# jeremy0330@book2020 ➜  Microsoft-Rewards-Farmer git:(service.20240627) ✗ ./foo.py
# [('bing', 0.5529), ('translate', 0.4742), ('search', 0.4065), ('word', 0.2395), ('any', 0.154)]

kw_model = KeyBERT()
keywords = kw_model.extract_keywords(doc)
print(keywords)


searches = kw_model.extract_keywords(
    doc, keyphrase_ngram_range=(1, 2), stop_words=["bing", "search", "searching"]
)

print(searches)
for e in searches:
    print(e[0])

term = str(random.choice(searches)[0])
print("---")
print(term)

# print(keywords)
# TODO: Ignore 'bing' and 'search'
