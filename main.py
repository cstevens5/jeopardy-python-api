from fastapi import FastAPI
import string
import spacy
import Levenshtein
from urllib.parse import unquote

app = FastAPI()

# load in the pre-trained spacy model
nlp = spacy.load('en_core_web_sm')

# ------------- HELPER FUNCTIONS --------------------------------

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

# function to determine if a string is a person or not
def is_person(text: str) -> bool:
    doc = nlp(text)
    for e in doc.ents:
        # if any tag is a person, then we will assume the entity is a person
        # this is safe to assume because of the specific condition in which we
        # are calling this function
        if e.label_ == "PERSON":
            return True
    return False

# function to determine if two strings are a close match
# Uses Levenshtein distance, which compares the number of single character edits
# needed to change one string into another
# a threshold measure will be used to determine if the strings are close
def is_close_match(user_input: str, correct_answer: str, threshold: float = 0.85) -> bool:
    # text will always be preprocessed first so no need to do any of that here
    ratio = Levenshtein.ratio(user_input, correct_answer)
    return ratio >= threshold


# function to call in the api route
# returns whether the user response is correct
def is_correct(user_response: str, correct_response: str) -> bool:
    # First preprocess the data
    user_words = preprocess(user_response)
    correct_words = preprocess(correct_response)

    # if these lists are exactly the same, then the user response is correct
    if user_words == correct_words:
        return True

    # join both lists back into strings
    user_string = " ".join(user_words)
    correct_string = " ".join(correct_words)
    
    # Next check if the correct response is a person's name -- if so we can check if
    # the user just entered that person's last name, and it will be marked correct

    # CONDITIONS:
    # 1) len(user_words) == 1 -> user only passed in the last name of a person
    # 2) len(correct_words) <= 2 -> correct answer may be of the form (first name, last name)
    # 3) is_person() -> check if the correct answer is a person
    if len(user_words) == 1 and len(correct_words) <= 2 and is_person(correct_string):
        # if the user entered the correct last name - the response is correrct
        if user_words[0] == correct_words[-1]:
            return True

    # NOTE: If the answer is a person who has a name with more than 2 words
    # (i.e. Vincent van Gogh), the user must enter the full name
    # This could be a source of improvement in the future

    # Finally, apply Levenshtein distance to determine how similar the user's
    # response is to the correct response -- this will allow the program to be less strict
    # in regards to typos and misspellings
    return is_close_match(user_string, correct_string)


# ------------- API ROUTES ---------------------------------------------

@app.get("/is-correct")
def check_answer_route(user_input: str, correct_input: str):
    # decode params
    user_input = unquote(user_input)
    correct_input = unquote(correct_input)
    return {"is_correct": is_correct(user_input, correct_input)}
