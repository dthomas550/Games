import sys, os, time, random
# Screen interaction
def clear(): print("\n"*50) # clears the scren
def wait(): input(" :") # pauses game, unil press 'enter'
def print_Back(): print("99 ) Go back"), print("100 ) Main menu") # prints menu options
def input_Back(x, pos): # check if input is 99 to go back, or 100 to go to main menu
    if x == 99: pos()
    elif x == 100: Startup()
    else: pass
def loading_Screen(x):
    for i in range(len(x)):
        print(x[i], end=" ")
        time.sleep(2)
    print("Done Loading...")
    # finds the length of the 'x' list, so it knows how long to loop.
    # then for each item in list it gives it the variable 'i'; just for one loop.
    # then on next loop it changes the 'i' value to the next item in list, then prints it out, each loop it pauses for 2sec


# Game Machanics
def game_Over(): # if you die, this asks you if you want to play again
    inp = input("Would you like to continue? > ")
    try: # this is if somebody inputs something that is not usable it goes to except, instead of crasing
        if inp in ('y', 'yes'): Startup() # if inputted 'y' or 'yes' it goes back to main menu
        else: # if anything else, it quits the game
            print("Thanks for playing!"), exit() # if you don't continue, it says bye
    except: pass

def error(): input("That didn't work : ") # simple error message


# makes sure this program doesn't run, if runned directly
if __name__ == '__main__': print("Shuld not be runned directly!")
else: print("Drake's Standard Library... Imported.")