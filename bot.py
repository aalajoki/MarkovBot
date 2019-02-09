import discord
import pickle
import re

# ID:
# Icon source:

client = discord.Client()

# Attempt to open the file that contains all learned words
try:
    with open("dict.txt","rb") as f:
        mainDict, firstwords = pickle.load(f)
        print("Dict file loaded")
# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:
        # Default dictionary. Will contain words that the bot "learns" from analyzing messages
        # These placeholder words are from sentences: "Apple is healthy" and "Cat is nice"
        mainDict = {"apple": {"is": 1}, "cat": {"is": 1}, "is": {"healthy": 1, "nice": 1}, "healthy": {"ENDSENTENCE" : 1}, "nice": {"ENDSENTENCE" : 1}}
        # Contains the words that can start a sentence
        firstwords = {"apple": 1,"cat": 1}
        # Save the default words into the newly created file
        pickle.dump([mainDict, firstwords], f)
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
        censor = ["@", "http", "ENDSENTENCE", "!debug-r", "!debug-u", "!update2"]
        
        pickle.dump(censor, f)
        print("Censor file created")




# The client event where someone in the discord server sends a message, allowing the bot to process it
@client.event
async def on_message(message):
    
    tempDict = mainDict
    # The bot will ignore messages from all bots, including itself
    if message.author.bot == True:
        print("Bot detected, ignoring message")
        return
    
            
    # DEBUG STUFF    
    if message.content == "!debug-r":
        print("-----------------")
        print("THE MAIN DICTIONARY:")
        for k, v in mainDict.items():
            print(k, v)
        print("-----------")
        print("THE FIRST WORDS:")
        for k, v in firstwords.items():
            print(k, v)
        print("-----------------")
    
    
    if message.content == "!debug-u":
        mainDict['apple']['is'] += 1
        with open("dict.txt", "wb") as f:
            pickle.dump([mainDict, firstwords], f)
            
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        
        
    #if message.content.startswith("!update2"):
    if message.content == "!update2":
        mainDict['apple']['is'] += 1
        mainDict.update({'boi':1})
        with open("dict.txt", "wb") as f:
            pickle.dump([mainDict, firstwords], f)
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
    
    
    
    
    # Check the message for censored words, ignore it if a censored word is discovered
    for censored in censor:
        if (re.search("(" + censored + ")", message.content, flags=0) is not None):
            print("Censor activated, ignoring message")
            return
    
    #Split the message into a list of the words
    messageWords = message.content.split()
    messageLength = len(messageWords)
    
    
    
    #for i in range(0, messageLength):
        
        # Ignore messages where there's consecutive duplicates in order to prevent probability skewing
        #currentWord = messageWords[i]
        
        #if (len(currentWord) > 9): # A maximum word length to prevent the bot from learning massive strings
        #    print("A too long word detected, ignoring message")
        #    return
            
        #if (i > 0): # Ignore the first word because there's nothing to compare it to
        #    print("Comparing " + currentWord + " and " + previousWord)
        #    if previousWord == currentWord:
        #        print("Consecutive duplicates detected, ignoring message")
        #        return
            
        # Ignore messages where a word appears more than 3 times in order to prevent probability skewing
        #count = messageWords.count(currentWord)
        #if count > 3:  
        #    print("The same word appears too many times, ignoring message")
        #    return
        #previousWord = currentWord
        
        
        
    # At this point, everything should be OK with the message and the bot will process it
    # Check the first word and either add it to the firstwords dictionary or increase its value by 1
    
    #if messageWords[0] not in firstwords:
        #new_word = messageWords[0]
        #firstwords.update({new_word: 1})
        #mainDict.update({new_word: 1})
    #else:
        #firstwords[messageWords[0]] += 1
    if messageWords[0] not in tempDict:
        tempDict[messageWords[0]] = {}
    
    try:
        firstwords[messageWords[0]] += 1
    except KeyError:
        firstwords[messageWords[0]] = 1
    
    
    for i in range(0, messageLength):
        # --- FILTERS AND CENSORS ---
        currentWord = messageWords[i]
        if (len(currentWord) > 9): # A maximum word length to prevent the bot from learning massive strings
            print("A too long word detected, ignoring message")
            return
            
        if (i > 0): # Ignore the first word because there's nothing to compare it to
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
            
            #for i in range(1, messageLength):
            if i > 0:
                #print("Adding word by index " + str(i))
                #previousWord = messageWords[i-1]
                #currentWord = messageWords[i]
                
                #print("PREVIOUS WORD: " + previousWord)
                #print("CURRENT WORD: " + currentWord)
                
                
                # Add the current word into the main dictionary if needed
                if currentWord not in tempDict:
                    tempDict[currentWord] = {}
                
                # Add the current word as one of the words that can follow the previous word
                try:
                    tempDict[previousWord][currentWord] += 1
                except KeyError:
                    tempDict[previousWord][currentWord] = 1
                
                #If word is the last of the message, add ENDSENTENCE to tag it as a word that can end a sentence    
                if currentWord == messageWords[messageLength - 1]:
                    try:
                        tempDict[currentWord]['ENDSENTENCE'] += 1
                    except KeyError:
                        tempDict[currentWord]['ENDSENTENCE'] = 1
                        
        previousWord = currentWord
        
    mainDict = tempDict
        
    # Save the new data into the files
    with open("dict.txt","wb") as f:
        pickle.dump([mainDict, firstwords], f)
        
        
        
        

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

client.run("NDgwODA0MjUyNzk3ODk0Njcy.Dzn-SQ.20mOWtrhA8R6BEFpxLyl3rf0LeE")