# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import pickle
import re
from random import randint


# These two dictionaries contain the words the bot "learns"
firstWords = {} # Contains the words that can start a sentence
mainDict = {} # Contains the rest of the words


description = "A silly bot that pretends to learn to speak."
bot = commands.Bot(command_prefix="¤", description=description)


# --- LOADING FILES ---

# Attempt to open the file that contains the dictionaries
try:
    with open("dict.txt","rb") as f:
        mainDict, firstWords = pickle.load(f)
        print("Dict file loaded")

# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:
        # Default dictionaries, used for testing if necessary
        # These placeholder words are from sentences: "Apple is healthy" and "Cat is nice"
        
        # mainDict = {"apple": {"is": 1}, "cat": {"is": 1}, "is": {"healthy": 1, "nice": 1}, "healthy": {"ENDSENTENCE" : 1}, "nice": {"ENDSENTENCE" : 1}}
        # firstWords = {"apple": 1,"cat": 1}
        
        # Save the dictionaries into the newly created files
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
        
        # The censored words are (and should be) as follows:
        # @, to prevent tagging and therefore directly notifying users
        # http, to prevent the bot from learning embedded links (such as linked images)
        # ENDSENTENCE, which the bot uses to tag words that are capable of ending a sentence
        # The bot's own commands, to keep the dictionary clean
        # Any words you wouldn't want the bot to say
        
        # IF YOU EDIT THE CENSOR LIST, REMEMBER TO DELETE THE OLD CENSOR.TXT AND RESTART THE BOT'S SCRIPT
        censor = ["@", "http", "ENDSENTENCE", "¤debug_r", "¤speak"]
        
        pickle.dump(censor, f)
        print("Censor file created")


# The event where someone in the discord server sends a message, allowing the bot to process it
@bot.event
async def on_message(message):
    
    # Makes bot commands work
    await bot.process_commands(message)
    
    global mainDict
    global firstWords
    
    # Using a temporary dictionary to prevent the bot from learning messages that do not pass the filters
    tempDict = mainDict
    
    
    # The bot will ignore messages from all bots, including itself
    if message.author.bot == True:
        print("Bot detected, ignoring message")
        return
    
    # Check the message for censored words, ignore it if a censored word is discovered
    for censored in censor:
        if (re.search("(" + censored + ")", message.content, flags=0) is not None):
            print("Censor activated, ignoring message")
            return
        
    
    # Split the message into a list of the words
    messageWords = message.content.split()
    messageLength = len(messageWords)
    
    
    # If the first word doesn't have its own nested dictionary in the main dictionary, add one
    if messageWords[0] not in tempDict:
        tempDict[messageWords[0]] = {}
    
    # Update first word's appearance count
    try:
        firstWords[messageWords[0]] += 1
    except KeyError:
        firstWords[messageWords[0]] = 1
    
    # Start going through each word in the message
    for i in range(0, messageLength):
        
        # --- FILTERS AND CENSORS ---
        currentWord = messageWords[i]
        
        # A maximum word length to prevent the bot from learning massive strings
        if len(currentWord) > 13:
            print("A too long word detected, ignoring message")
            return
        
        # Ignore the first word because there's nothing to compare it to    
        if i > 0:
            # Ignore messages where the same word appears twice in a row to prevent probability skewing
            if previousWord == currentWord:
                print("Consecutive duplicates detected, ignoring message")
                return
            
        # Ignore messages where a word appears more than 3 times in order to prevent probability skewing
        count = messageWords.count(currentWord)
        if count > 4:  
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
        
    # tempDict is temporary no longer
    mainDict = tempDict
        
    # Update the files
    with open("dict.txt","wb") as f:
        pickle.dump([mainDict, firstWords], f)
    
    # Giving the bot a random chance to speak on its own
    if randint(1, 29) == 1:
        sentence = await formulate()
        await message.channel.send(sentence)
    


    

# The function for formulating sentences
async def formulate():
    sentence = "" # The sentence which will be formulated
    previousWord = "" # The previous word that will be used to choose the next one
    wordLimit = 79 # 80 minus the first word
    
    # Choosing the first word (randomly, of course)
    wordRandomizer = randint(1, sum(firstWords.values()))
    
    for key, value in firstWords.items():
        
        wordRandomizer -= value
        if wordRandomizer <= 0:
            # The word has been found and will be added to the sentence
            sentence += key + " "
            previousWord = key
            break
        
        
    # Choosing the next words (randomly, of course)
    looping = True
    while looping:
        nestedDict = mainDict[previousWord] # Find the word's nested dictionary, which tells us which words can go next
        nestedDictValues = sum(nestedDict.values())
        if nestedDictValues != 1:
            wordRandomizer = randint(1, nestedDictValues) # For choosing one of the words

            for key, value in nestedDict.items():
                # For each next word candidate, their appearance count is reduced from the randomized number
                wordRandomizer -= value
                # Once the randomized number is zero or less, the word will be chosen
                if wordRandomizer <= 0:
                    # If the chosen word happens to be ENDSENTENCE, the formulation will end
                    if key == "ENDSENTENCE":
                        looping = False
                        break
                    else:
                        # Add the chosen word to the sentence
                        sentence += key + " "
                        
                        # Check the word limit
                        wordLimit -= 1
                        if wordLimit == 0:
                            looping = False
                            
                        previousWord = key
                        break
        else:
            break
    
    # Return the finished sentence
    return sentence
    
    

# --- COMMANDS ---
    
# A command to make the bot speak manually in the server where the command was used
@bot.command()
async def speak(ctx):
    sentence = await formulate()
    await ctx.send(sentence)
   
# A debug command that prints the dictionary contents into the console
@bot.command()
async def debug_r():
    print("-----------------")
    print("THE MAIN DICTIONARY:")
    for k, v in mainDict.items():
        print(k, v)
    print("-----------")
    print("THE FIRST WORDS:")
    for k, v in firstWords.items():
        print(k, v)
    print("-----------------")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    game = discord.Game("¤speak")
    await bot.change_presence(activity=game)

bot.run("BOT TOKEN HERE")