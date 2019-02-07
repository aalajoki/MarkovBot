import discord
import pickle
import re

# ID:
# Icon source:

client = discord.Client()

# Attempt to open the file that contains all learned words
try:
    with open("dict.txt","rb") as f:
        maindict, firstwords = pickle.load(f)
        print("Dict file loaded")
# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:

        # Default dictionary. Will contain words that the bot "learns" from analyzing messages
        # These placeholder words are from sentences: "Apple is healthy" and "Cat is nice"
        maindict = {"apple": {"is": 1}, "cat": {"is": 1}, "is": {"healthy": 1, "nice": 1}, "healthy": {"ENDSENTENCE" : 1}, "nice": {"ENDSENTENCE" : 1}}
        # Contains the words that can start a sentence
        firstwords = {"apple": 1,"cat": 1}
        # Save the default words into the newly created file
        pickle.dump([maindict, firstwords], f)
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
        censor = ["ENDSENTENCE", "http", "@"]
        pickle.dump(censor, f)
        print("Censor file created")


# The client event where someone in the discord server sends a message, allowing the bot to process it
@client.event
async def on_message(message):
    # The bot will ignore its own messages
    if message.author == client.user:
        return
    
    # Check the message for censored words, ignore it if a censored word is discovered
    for censored in censor:
        if (re.search("(" + censored + ")", message.content, flags=0) is not None):
            print("Censor activated, ignoring message")
            return
    
    #Split the message into a list of the words
    messagewords = message.content.split()
    
    
    for i in range(0, len(messagewords)):
        # Ignore messages where there's consecutive duplicates in order to prevent probability skewing
        currentWord = messagewords[i]
        if (i > 0):
            print("Comparing " + currentWord + " and " + previousWord)
            if previousWord == currentWord:
                print("Consecutive duplicates detected, ignoring message")
                return
            
        # Ignore messages where a word appears more than 3 times in order to prevent probability skewing
        count = messagewords.count(currentWord)
        if count > 3:  
            print("The same word appears too many times, ignoring message")
            return
        previousWord = currentWord
        
    # At this point, everything should be OK with the message
    # Check the first word and either add it to the firstwords dictionary or increase its value by 1
    if messagewords[0] not in firstwords:
        new_word = str(messagewords[0])
        firstwords.update({new_word: 1})
        maindict.update({new_word: 1})
    else:
        firstwords[messagewords[0]] += 1
    
    
    # Go through each word if there's more than 1
    if (len(messagewords) > 1):
        for i in range(1, len(messagewords)):
            print("Adding word by index " + str(i))
            if messagewords[i] not in maindict:
                new_word = str(messagewords[i])
                maindict.update({new_word: 1})
            else:
                maindict[messagewords[i]] += 1
            #If word is last, add ENDSENTENCE
    #else:
        #Add ENDSENTENCE to the first word if it's the only one
        
    # Save the new data into the files
    with open("dict.txt","wb") as f:
        pickle.dump([maindict, firstwords], f)
        
        
        
        
        
        
    # DEBUG STUFF    
    if message.content.startswith("!debug-r"):
        for k, v in maindict.items():
            print(k, v)
        print("---------")
        for k, v in firstwords.items():
            print(k, v)
    
    
    if message.content.startswith("!debug-u"):
        maindict['apple']['is'] += 1
        with open("dict.txt", "wb") as f:
            pickle.dump([maindict, firstwords], f)
            
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        
        
    if message.content.startswith("!update2"):
        maindict['apple']['is'] += 1
        maindict.update({'boi':1})
        with open("dict.txt", "wb") as f:
            pickle.dump([maindict, firstwords], f)
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        
        

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

client.run("BOT'S DISCORD TOKEN HERE")