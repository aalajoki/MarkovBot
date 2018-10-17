import discord
import pickle
import re

TOKEN = '' # Personal discord bot token here

# ID:
# Icon source:

client = discord.Client()

# Attempt to open the file that contains all learned words, the first words and the censor list
try:
    with open("dict.txt") as f:
        dict_txt = "dict.txt"
    with open("dict.txt","rb") as f:
        dict, firstwords, censor = pickle.load(f)
        
# If file is not found, create a new one
except FileNotFoundError:
    with open("dict.txt","wb") as f:
        dict_txt = "dict.txt"

        # Default dictionary. Will contain words that the bot "learns" from analyzing messages
            #From sentences: "Apple is healthy" and "Cat is nice"
        dict = {'apple': {'is': 1}, 'cat': {'is': 1}, 'is': {'healthy': 1, 'nice': 1}}
        
        # Contains the words that can start a sentence
        firstwords = {'apple': 1,'cat': 1}
        
        # Contains the list of words that will cause the bot to ignore the message
        censor = ["boi"]
        
        # Save the default words into the newly created file
        pickle.dump([dict, firstwords, censor], f)


        


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
            #return (ignore message)
        #chopped_words = message.content.split()
        
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
    
    
    if message.content.startswith('!debug-u'):
        dict['apple']['is'] += 1
        with open("dict.txt", "wb") as f:
            pickle.dump([dict, firstwords, censor], f)
            
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        
        
        
        
        
    if message.content.startswith('!update2'):
        dict['apple']['is'] += 1
        dict.append({'boi':1})
        with open("dict.txt", "wb") as f:
            pickle.dump([dict, firstwords, censor], f)
        msg = "Updated".format(message)
        await client.send_message(message.channel, msg)
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
# Check if dict.txt exists, then create / read it   ??

client.run(TOKEN)