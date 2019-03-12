import discord
from discord.ext import commands
import pickle
import re
from random import randint

# ID:
# Icon source:

#client = discord.Client()

# Contains the words that can start a sentence
firstWords = {}
# Contains the rest of the words
mainDict = {}


description = "A silly bot that pretends to learn to speak."
bot = commands.Bot(command_prefix="¤", description=description)


# Attempt to open the file that contains all learned words
try:
    with open("dict.txt","rb") as f:
        mainDict, firstWords = pickle.load(f)
        print("Dict file loaded")
        
# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:
        # Default dictionary. Will contain words that the bot "learns" from analyzing messages
        # These placeholder words are from sentences: "Apple is healthy" and "Cat is nice"
        #mainDict = {"apple": {"is": 1}, "cat": {"is": 1}, "is": {"healthy": 1, "nice": 1}, "healthy": {"ENDSENTENCE" : 1}, "nice": {"ENDSENTENCE" : 1}}
        
        # Contains the words that can start a sentence
        #firstWords = {"apple": 1,"cat": 1}
        
        # Save the default words into the newly created file
        pickle.dump([mainDict, firstWords], f)
        print("Dict file created")

# Attempt to open the file that contains the censored words
try:
    with open("censor.txt","rb") as f:
        censor = pickle.load(f)
    print("Censor file loaded")
    print(censor)
    
# If file is not found, create a new one
except FileNotFoundError:
    with open("censor.txt","wb") as f:
        # The list of words that will cause the bot to ignore the message, AKA the censored words
        
        # The censored words are (and maybe should be) as follows:
        # @, to prevent tagging and therefore directly notifying users
        # http, to prevent the bot from learning embedded links (such as linked images)
        # ENDSENTENCE, which the bot uses to tag words that are capable of ending a sentence
        # The bot's own commands, to keep the dictionary clean
        
        # Naturally, any offensive words you wouldn't want the bot to say should be added
        
        #IF YOU EDIT THE CENSOR LIST, REMEMBER TO DELETE THE OLD CENSOR.TXT AND RESTART THE BOT'S SCRIPT
        censor = ["@", "http", "ENDSENTENCE", "!debug-r", "!debug-u", "!update2", "¤speak"]
        
        pickle.dump(censor, f)
        print("Censor file created")




# The event where someone in the discord server sends a message, allowing the bot to process it
@bot.event
async def on_message(message):
    
    # Makes bot.commands work
    await bot.process_commands(message)
    
    # Using a temporary dictionary to prevent the bot from learning messages that do not pass the filters
    global mainDict
    global firstWords
    
    tempDict = mainDict
    # The bot will ignore messages from all bots, including itself
    if message.author.bot == True:
        print("Bot detected, ignoring message")
        return
    
            
    # DEBUG COMMANDS
    
    if message.content == "!debug-r":
        print("-----------------")
        print("THE MAIN DICTIONARY:")
        for k, v in mainDict.items():
            print(k, v)
        print("-----------")
        print("THE FIRST WORDS:")
        for k, v in firstWords.items():
            print(k, v)
        print("-----------------")
    
    
    
    # Check the message for censored words, ignore it if a censored word is discovered
    for censored in censor:
        if (re.search("(" + censored + ")", message.content, flags=0) is not None):
            print("Censor activated, ignoring message")
            return
    
    # Split the message into a list of the words
    messageWords = message.content.split()
    messageLength = len(messageWords)
    
    
    
    if messageWords[0] not in tempDict:
        tempDict[messageWords[0]] = {}
    
    try:
        firstWords[messageWords[0]] += 1
    except KeyError:
        firstWords[messageWords[0]] = 1
    
    # Start going through each word in the message
    for i in range(0, messageLength):
        
        # --- FILTERS AND CENSORS ---
        currentWord = messageWords[i]
        
        # A maximum word length to prevent the bot from learning massive strings
        if len(currentWord) > 11:
            print("A too long word detected, ignoring message")
            return
        
        # Ignore the first word because there's nothing to compare it to    
        if i > 0:
            # Ignore messages where the same word appears twice in a row to prevent probability skewing
            print("Comparing " + currentWord + " and " + previousWord)
            if previousWord == currentWord:
                print("Consecutive duplicates detected, ignoring message")
                return
            
        # Ignore messages where a word appears more than 3 times in order to prevent probability skewing
        count = messageWords.count(currentWord)
        if count > 3:  
            print("The same word appears too many times, ignoring message")
            return
        
        
        # --- STORING WORDS ---
        
        # Go through each word if there's more than 1
        if (messageLength > 1):
            # Skip over the first word since it has already been processed
            if i > 0:
                # Add the current word into the main dictionary if needed
                if currentWord not in tempDict:
                    tempDict[currentWord] = {}
                
                # Add the current word as one of the words that can follow the previous word
                try:
                    tempDict[previousWord][currentWord] += 1
                except KeyError:
                    tempDict[previousWord][currentWord] = 1
                
                # If word is the last of the message, add ENDSENTENCE to tag it as a word that can end a sentence    
                if currentWord == messageWords[messageLength - 1]:
                    try:
                        tempDict[currentWord]["ENDSENTENCE"] += 1
                    except KeyError:
                        tempDict[currentWord]["ENDSENTENCE"] = 1
        else:
            try:
                tempDict[currentWord]["ENDSENTENCE"] += 1
            except KeyError:
                tempDict[currentWord]["ENDSENTENCE"] = 1
                        
        previousWord = currentWord
        
    mainDict = tempDict
        
        
        
    # Update the files
    with open("dict.txt","wb") as f:
        pickle.dump([mainDict, firstWords], f)
        
    # ADD RANDOM CHANCE TO SPEAK (CALL FORMULATE())
        
    


@bot.command()
async def speak():
    await formulate()
    #ctx.send("asd")
    


async def formulate():
    sentence = ""
    previous_word = ""
    
    # Choosing the first word
    wordRandomizer = randint(1, sum(firstWords.values()))
    
    #print("  --START RANDOM--")
    #print("      firstWords sum = " + str(sum(firstWords.values())))
    #print("      random int = " + str(wordRandomizer))
    #print("  --END RANDOM--")
    
    for key, value in firstWords.items():
        #print("random before: " + str(wordRandomizer))
        #print("value of " + key + ": " + str(value))
        wordRandomizer -= value
        #print("random after: " + str(wordRandomizer))
        if wordRandomizer <= 0:
            sentence += key + " "
            previous_word = key
            #print("  chosen word = " + key)
            break
        
        
    # Choosing the next words
    looping = True
    while looping:
        nestedDict = mainDict[previous_word]
        wordRandomizer = randint(1, sum(nestedDict.values()))
        print("DICT: " + str(nestedDict) + " WITH SUM: " + str(sum(nestedDict.values())))
        
        for key, value in nestedDict.items():
            print("KEY: " + key + ", VALUE: " + str(value))
            wordRandomizer -= value
            print("RANDOMIZER: " + str(wordRandomizer))
            print("*********")
            if wordRandomizer <= 0:
                if key == "ENDSENTENCE":
                    looping = False
                    break
                else:
                    sentence += key + " "
                    previous_word = key
                    break
    
        
    await bot.say(sentence)
    #ctx.send("asd")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    await bot.change_presence(game=discord.Game(name="a game"))

bot.run("NDgwODA0MjUyNzk3ODk0Njcy.D2hmYw.7BR20tMprRG2ytfqFIra3beAfzM")