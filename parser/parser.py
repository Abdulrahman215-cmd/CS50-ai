import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | DP VP | NP VP Conj VP | NP VP Conj NP VP | NP VP Conj VP NP
AP -> Adj | Adj AP
DP -> Det NP
NP -> N | AP NP | N PP | N Adv
PP -> P NP | P DP
VP -> V | Adj VP | V DP | V NP | V Adv | V PP | V NP PP | V PP Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    list_words = []
    splitted_sentence = nltk.word_tokenize(sentence)
    for word in splitted_sentence:
        lower_words = word.lower() 
        if any(c.isalpha() for c in lower_words):
            list_words.append(lower_words)
    return list_words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    contains_np = False
    for current_subtrees in tree.subtrees():
        contains_np = False
        if current_subtrees.label() == "NP":
            for other_subtrees in current_subtrees.subtrees():
                if other_subtrees.label() == "NP":
                    if other_subtrees != current_subtrees:
                        contains_np = True
                        break
            if contains_np == False:
                if current_subtrees not in chunks:
                    chunks.append(current_subtrees)

    return chunks
    

if __name__ == "__main__":
    main()
