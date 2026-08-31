import json # lets us read the quiz questions from a json file
import random # lets us randomize the order of the quiz questions
from datetime import datetime # lets us get the current date and time for the quiz results

# load the quiz questions from the json file
def load_questions(filename):
    # open the file and read the questions
    f = open(filename, 'r')
    questions = json.load(f) # turns the file contents into a list of dictionaries
    f.close()
    return questions

# print a question and its answer choices
def display_question(question, choices):
    print() # blank line for spacing
    print(question)
    # loop through each letter and its answer option
    for letter in choices:
        print(" " + letter + ") " + choices[letter]) # print the letter and the answer option

# keep asking until user types a valid answer or 5050
def get_valid_answer(valid_options):
    valid_options = list(valid_options)
    while True:
        answer = input("Your answer: ").strip().lower()
        if answer in valid_options:
            return answer
        else:
            print("That is not a valid answer. Please try again.")

# remove 2 wrong answers for the 50/50 lifeline
def fifty_fifty(choices, correct_answer):
    # make a list of the wrong answer letters
    wrong_answers = []
    for letter in choices:
        if letter != correct_answer:
            wrong_answers.append(letter)

    # randomly select 2 wrong answers to remove
    removed_answers = random.sample(wrong_answers, 2)

    # build a new choices list without those 2 wrong answers
    new_choices = {}
    for letter in choices:
        if letter not in removed_answers:
            new_choices[letter] = choices[letter]

    return new_choices

# save the score to a text file
def save_score(username, score, total): # added username parameter to save the player's name along with the score
    # get the current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # open scores.txt in append mode and write the score with the timestamp
    f = open("scores.txt", "a")
    f.write(f"{timestamp} - Score: {score}/{total}\n")
    f.close()

# load users from users.json
def load_users():
    try:
        f = open("users.json", "r")
        users = json.load(f)
        f.close()
        return users
    except:
        return{} # if file does not exist yet, start with empty dict
    
# save users to users.json
def save_users(users):
    f = open("users.json", "w")
    json.dump(users, f)
    f.close()

# find the grand champion (user with the highest score)
def get_champion(users):
    champion = None
    highest_score = -1
    for username in users:
        if users[username]["high_score"] > highest_score:
            champion = username
            highest_score = users[username]["high_score"]
    return champion, highest_score

# main function to run the quiz
print("Welcome to the Quiz Game!")
print()

# load existing users
users = load_users()

# ask for the player's username
username = input("Please enter your username: ")

# check if user exists, if not create a new entry for them
if username not in users:
    print(f"Welcome, {username}! It looks like you are a new player. Let's get started!")
    users[username] = {"high_score": 0} # initialize new user with a high score of 0
else:
    print(f"Welcome back, {username}! Your current high score is {users[username]['high_score']}.")

print("Answer each question by typing the letter of your choice.")
print("You have one 50/50 lifeline. Type 5050 to use it on a question.")    

# load questions from the json file and shuffle them
questions = load_questions("questions.json")
random.shuffle(questions)

score = 0 # start with a score of 0
used_5050 = False # player has not used the 50/50 lifeline yet

# loop through each question one at a time
for i in range(len(questions)):

    # get the current questions
    q = questions[i]
    correct = q["answer"].strip().lower() # the correct answer letter
    choices = q["choices"].copy() # copy so we can modify for 50/50

    # show the question
    display_question("Q" + str(i+1) + ": " + q["question"], choices)

    # ask for the player's answer
    print("(Type 5050 to use your 50/50 lifeline)")
    answer = input("Your answer: ")
    answer = answer.strip().lower() # remove extra spaces and convert to uppercase

    # check if the player wants to use the 50/50 lifeline
    if answer == "5050":
        if used_5050 == False:
            used_5050 = True # mark the lifeline as used
            choices = fifty_fifty(choices, correct) # get the new choices with 2
            print("50/50 lifeline used! Here are your remaining options:")
            display_question("Q" + str(i+1) + ": " + q["question"], choices)
            answer = get_valid_answer(choices.keys()) # ask for a valid answer from the remaining
        else:
            print("You have already used your 50/50 lifeline. Please choose an answer.")
            answer = get_valid_answer(choices.keys()) # ask for a valid answer from the original choices

    # if they typed something invalid (not 5050 and not a/b/c/d)
    elif answer not in choices:
        print("That is not a valid answer. Please choose from the options.")
        answer = get_valid_answer(choices.keys()) # ask for a valid answer from the original choices

    # check if the answer is correct
    if answer == correct:
        print("Correct!")
        score = score + 1 # increase the score for a correct answer
    else:
        print("Wrong! The correct answer was " + correct + ") " + q["choices"][correct])

# quiz is over, show the final score
print()
print("Quiz completed!")
print(f"Your final score is: {score}/{len(questions)}")

# check if this is the player's new high score and update if so
if score > users[username]["high_score"]:
    print(f"Congratulations, {username}! You have a new high score!")
    users[username]["high_score"] = score
else:
    print(f"Your high score remains: {users[username]['high_score']}")

# save the updated users back to the json file
save_users(users)

# save the score to a text file
save_score(username, score, len(questions))
print("Your score has been saved to scores.txt")

# show the grand champion
champion, best_score = get_champion(users)
print()
print(f"The grand champion is {champion} with a high score of {best_score}!")
