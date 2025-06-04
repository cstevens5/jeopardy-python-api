from fastapi import FastAPI
import re
import string
import nltk
import spacy

app = FastAPI()


# function to preprocess a string of text
# -- First NLP Step --
def preprocess(text: str) -> list[str]:
    # 1. Lowercase
    text = text.lower()

    # 2. Remove Punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 3. Tokenize
    words = text.split(" ")

    # 4. Remove extra white space
    words = [word.replace(" ", "") for word in words]

    # define a set of stopwords
    # the stopwords built into spacy are too much for my purposes
    stopwords = set(["the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or", "by", "with"]);

    # 5. Remove Stopwords
    words = [word for word in words if word not in stopwords]

    # Now return the preprocessed list of words
    return words


# function to call in the api route
# returns whether the user response is correct
def is_correct(user_response: str, correct_response: str) -> bool:
    # First preprocess the data
    user_words = preprocess(user_response)
    correct_words = preprocess(correct_response)

    # if these lists are exactly the same, then the user response is correct
    if user_words == correct_words:
        return True
    
    # Next check if the correct response is a person's name -- if so we can check if
    # the user just entered that person's last name, and it will be marked correct

    if len(user_words) == 1:
        # this must be the case if the user only entered a person's last name
        # if the user entered the full name, it would be caught in the check above
        pass

    # Finally, apply comparison/similarity techniques to determine how similar the user's
    # response is to the correct response -- this will allow the program to be less strict
    # in regards to typos and misspellings
