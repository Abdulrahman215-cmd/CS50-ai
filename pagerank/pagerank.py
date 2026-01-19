import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    corps = len(corpus)

    probability = dict()
    for pag1 in corpus:
        probability[pag1] = 0

    if len(corpus[page]) > 0:
        for pag1 in corpus:
            formula_1 = (1 - damping_factor) / corps
            probability[pag1] += formula_1
            # cs50 ai told me to seperate the loops and use corpus[page] and use len(corpus[page])
        for pag1 in corpus[page]:
            formula_2 = damping_factor / len(corpus[page])
            probability[pag1] += formula_2

    elif len(corpus[page]) == 0:
        equal = 1 / corps
        for pag1 in corpus:
            probability[pag1] += equal

    total = []
    for pag1 in corpus:
        total.append(probability[pag1])

    summed = sum(total)
    for pag1 in corpus:
        probability[pag1] = probability[pag1] / summed

    return probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probability = dict()
    for pag1 in corpus:
        probability[pag1] = 0

    # cs50 ai told me to use random.choices(list(corpus.keys())) but i removed the s in choices and fixed a problem i had
    current_page = random.choice(list(corpus.keys()))
    for i in range(n):
        transition = transition_model(corpus, current_page, damping_factor)
        # cs50 ai told me to use exactly weights = transition.values()
        random_choice = random.choices(list(corpus.keys()), weights=transition.values())
        current_page = random_choice[0]
        probability[current_page] += 1

    total = []
    for pag1 in corpus:
        total.append(probability[pag1])

    summed = sum(total)
    for pag1 in corpus:
        probability[pag1] = probability[pag1] / summed

    return probability


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    corps = len(corpus)
    converge = True
    page_rank = dict()
    new_page_rank = dict()

    for page1 in corpus:
        page_rank[page1] = 1 / corps
    while converge == True:
        max_difference = 0
        all_converged = True

        for page in corpus:
            formula_1 = (1 - damping_factor) / corps

            formula_2 = 0
            for linker in corpus:
                if len(corpus[linker]) == 0:
                    formula_2 += damping_factor * page_rank[linker] / corps
            for linker in corpus:
                # cs50 ai told me to use this if statement
                if page in corpus[linker]:
                    formula_2 += damping_factor * page_rank[linker] / len(corpus[linker])

             # cs50 ai told me to place this exactly here
            formula_3 = formula_2 + formula_1
            new_page_rank[page] = formula_3

        total = []
        for pag1 in corpus:
            total.append(new_page_rank[pag1])

        summed = sum(total)
        for pag1 in corpus:
            new_page_rank[pag1] = new_page_rank[pag1] / summed

        for page in corpus:
            # cs50 ai told me to use the if statement and max_difference and helped me with updating max_difference
            if abs(new_page_rank[page] - page_rank[page]) > max_difference:
                max_difference = abs(new_page_rank[page] - page_rank[page])
        if max_difference < 0.001:
            all_converged = False

        converge = all_converged
        # cs50 ai told me to use to use this exact line below
        page_rank = new_page_rank.copy()

    return page_rank


if __name__ == "__main__":
    main()
