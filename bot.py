import discord
import pickle
import re

TOKEN = '' # Personal discord bot token here

# ID:
# Icon source:

client = discord.Client()

# Attempt to open the file that contains all learned words, the first words and the censor list
try:
    with open("dict.txt","rb") as f:
        dict, firstwords = pickle.load(f)
# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:

        # Default dictionary. Will contain words that the bot "learns" from analyzing messages
            #From sentences: "Apple is healthy" and "Cat is nice"
        dict = {'apple': {'is': 1}, 'cat': {'is': 1}, 'is': {'healthy': 1, 'nice': 1}}
        
        # Contains the words that can start a sentence
        firstwords = {'apple': 1,'cat': 1}
        
        # Save the default words into the newly created file
        pickle.dump([dict, firstwords], f)



try:
    with open("censor.txt","rb") as f:
        censor = pickle.load(f)   
# If file is not found, create a new one
except FileNotFoundError:
    with open("censor.txt","wb") as f:
        # Contains the list of words that will cause the bot to ignore the message
        censor = ["boi, http"]
        pickle.dump(censor, f)



@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    
    # Check message for censored words
    for word in censor:
        if (re.search("(" + word + ")", message.content, flags=0) != None):
            msg = "Censor activated".format(message)
            
        else:
            msg = "All clear".format(message)
            messagewords = message.content.split()
            
            # Check the first word of the message and either add it to the list or increase its value by 1
            if messagewords[0] not in firstwords:
                new_word = str(messagewords[0])
                firstwords.update({new_word: 1})
                dict.update({new_word: 1})
            else:
                firstwords[messagewords[0]] += 1
                
            for i in range(1, len(messagewords) + 1):
                if messagewords[i] not in dict:
                    new_word = str(messagewords[i])
                    dict.update({new_word})
                else:
                    #
                    #firstwords[messagewords[0]] += 1
            # Save the new data into the files
        
        #Ignore sentences with the same word more than two times to avoid skewing the word probabilities
        #elif (has more than 2 of the same word):
            #return (ignore message)
        #else:
            # Chop the sentence up and add the words to the dictionaries
            
    await client.send_message(message.channel, msg)
        
        
        
    # Print dictionary contents to the console when a user sends "!debug-r" message
    if message.content.startswith('!debug-r'):
        for k, v in dict.items():
            print(k, v)
        print("---------")
        for k, v in firstwords.items():
            print(k, v)
    
    
    if message.content.startswith('!debug-u'):
        dict['apple']['is'] += 1
        with open("dict.txt", "wb") as f:
            pickle.dump([dict, firstwords], f)
            
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        
        
        
        
        
    if message.content.startswith('!update2'):
        dict['apple']['is'] += 1
        dict.append({'boi':1})
        with open("dict.txt", "wb") as f:
            pickle.dump([dict, firstwords], f)
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)