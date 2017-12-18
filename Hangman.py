import requests
import re
from collections import Counter
import string
import time
import pandas as pd

#scrape names from celeb mafia
url = "http://celebmafia.com/celebrity-list/"
response = requests.get(url)
html_doc = response.text
pattern = "\n<li><a title=(.*?) href="
names = re.findall(pattern, html_doc)

#create clean list of names
clean = []
for name in names:
    name=name.upper().replace('"', '')
    if 'AWARDS' not in name:
        done=False
        for letter in name:
            if letter.isalpha() == False and letter != " ":
                done=True
                break
        if not done:
            pieces = name.split(" ")
            if len(pieces) == 2:
                clean.append(pieces)

def start():
    """
    Prints instructions, accepts the number of letters, refines the database and produces a visual output of the name structure.
    """
    print("\n-------------------------------------")
    print("\nHello and welcome to Hangman Challenge! If at any point you can't handle the heat, press control+C to exit.")
    print("\nComputer challenges you to play hangman on its favourite topic: female A listers. Computer believes it can recognise the name of any female celeb you choose by taking 3 guesses at the letters it contains, hangman style.")
    print("\nShould you accept this challenge, pick a celeb and enter the number of letters in their first and last names, separated by a comma (for example, if you chose Britney Spears you would enter 7,6).")
    global count
    count=0
    inp = raw_input("\n>>Your answer here: ")
    first, second = inp.split(",")
    first, second = int(first), int(second)

    #create list of structural matches
    hits = []
    for name in clean:
        if len(name[0]) == first and len(name[1]) == second:
            hits.append(name)

    #set up pandas structure for visual output
    structure = ("__,")*first + " ," + ("__,")*second
    spacers = list(structure.split(","))[:-1]
    col_names = range(1,first+second+1)
    col_names.insert(first, " ")
    global df
    df = pd.DataFrame(columns = col_names, index=range(0,2))
    df.iloc[0] = spacers
    df.iloc[1] = col_names
    print("\n" + df.to_string(header=None, index=False))
    guess_letter(hits)

def guess_letter(list_of_lists):
    """
    Calculates the most common letter in the database and records the number of previous guesses.
    """
    global guess
    d = Counter(string.ascii_uppercase)
    for full_name in list_of_lists:
        for name in full_name:
            for letter in name:
                d.update(letter)
    i=1
    while d.most_common(i)[-1][0] in df.iloc[0].values:
        i+=1
    guess = d.most_common(i)[-1][0]
    print("\nComputer is thinking...")
    time.sleep(2)
    global count
    count+=1
    print("\nComputer guesses: " + str(guess) + " (" + str(count) + " out of 3 guesses used)")
    hits = list_of_lists #ensures that "refined" lists are stored before refine function is called again
    refine(hits)

def refine(hits):
    """
    Takes a database of names and refines it based on the success of the letter guess.
    """
    refined = []
    print("\nIs this letter in your name? y/n")
    correct = raw_input(">>Your answer here: ")
    if correct not in ("n", "N", "no", "No", "y", "Y", "yes", "Yes"):
        correct = raw_input("\n>>Please answer in the form y/n: ")

    #remove names with an incorrect guess in
    if correct in ("n", "N", "no", "No"):
        if count < 3:
            for name in hits:
                if guess not in name[0] and name[1]:
                    refined.append(name)
        elif count ==3:
            print("\nDamn, computer couldn't guess your celeb in 3 moves! Surely you couldn't pull that off again...")
            play_again()

    #only keep names with a correct guess in at correct positions
    elif correct in ("y", "Y", "yes", "Yes"):
        print("\nPlease enter the numerical position(s) that this letter appears at, seperated by commas if more than once.")
        answer = raw_input(">>Your answer here: ")
        if "," in answer:
            positions = sorted(int(num)-1 for num in answer.split(","))
        else:
            positions = [int(answer)-1]
        for name in hits:
            concat = name[0] + name[1]
            guess_indices = [m.start() for m in re.finditer(guess, concat)]
            if guess_indices == positions:
                refined.append(name)
        for num in positions: #fill in pandas structure with correct guesses
            df.loc[0, num+1] = guess
        print("\n"+df.to_string(header=None, index=False))

    #guess the whole name if only one name left in the database
    if len(refined) == 1:
        print("\nComputer guesses that you chose " + str(refined[0][0]) + " " + str(refined[0][1]))
        print("\nWas this correct? y/n")
        answer = raw_input(">>Your answer here: ")
        if answer in ("y", "Y", "yes", "Yes"):
            print("\nHurrah! Computer knew you couldn't beat it..." )
            play_again()
        elif answer in ("n", "N", "no", "No"):
            oops()
    elif len(refined) == 0:
        oops()
    else:
        guess_letter(refined)

def oops():
    """Prints error message when there are no names left to guess in the database."""
    print("\nOh dear, your celebrity isn't on the A list! She needs to be be female, famous and alive.")
    play_again()

def play_again():
    """Re-runs or exits the programme."""
    print("\nWant to play again? y/n")
    answer = raw_input(">>Your answer here: ")
    if answer in ("y", "Y", "yes", "Yes"):
        start()
    elif answer in ("n", "N", "no", "No"):
        print("\nThanks for playing, come and lose another time!\n")
        print("-------------------------------------")
        exit()

start()
