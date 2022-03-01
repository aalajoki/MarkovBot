# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import re
from random import randint
import redis
# Contains the list of censored words, the max word and sentence length and the discord bot token
import config

db = redis.Redis(
    host = config.redisHost,
    port = config.redisPort,
    charset = 'utf-8',
    decode_responses = True
)

description = 'A silly bot that pretends to learn to speak.'
bot = commands.Bot(command_prefix = '¤', description = description)

@bot.event
async def on_message(message):
    # Makes the bot commands work
    await bot.process_commands(message)

    # Ignore messages from bots, including itself
    if message.author.bot == True:
        return
    
    # Check the message for censored words, ignore if a censored word is discovered
    for censoredWord in config.censored:
        if (re.search('(' + censoredWord + ')', message.content, flags=0) is not None):
            return

    # Actually process the message
    listen(message.content)

    # Random chance to trigger an automatic response
    if randint(1, 29) == 1:
        sentence = formulateSentence()
        await message.channel.send(sentence)

def listen(message):
    messageWords = message.split()
    messageLength = len(messageWords)
    # Not sure why messages sometimes do not have content
    try:
        firstWord = messageWords[0]
    except IndexError:
        return

    if (len(firstWord) >= config.maxWordLength):
        return

    db.sadd('FirstWords', firstWord)

    try:
        if (len(messageWords[1]) >= config.maxWordLength):
            return
        db.sadd(firstWord, messageWords[1])
    except IndexError:
        db.sadd(firstWord, 'ENDSENTENCE')

    for i in range(1, messageLength):
        try:
            if (len(messageWords[i + 1]) > config.maxWordLength):
                return
            db.sadd(messageWords[i], messageWords[i + 1])
        except IndexError:
            db.sadd(messageWords[i], 'ENDSENTENCE')

# The function for formulating sentences
def formulateSentence(userWords = None):
    sentence = ''
    # argument OR db.srandmember()
    # firstWord = db.srandmember('FirstWords')

    print(userWords)

    if userWords:
        firstWord = userWords[-1]
        sentence = ' '.join(userWords)
    else:
        firstWord = db.srandmember('FirstWords')

    sentenceLength = 1

    previousWord = firstWord

    while True:
        nextWord = getNextWord(previousWord)

        if (nextWord == 'ENDSENTENCE' or nextWord is None):
            return sentence
        else:
            sentence += ' ' + nextWord
            previousWord = nextWord
            sentenceLength += 1
            if (sentenceLength >= config.maxSentenceLength):
                return sentence

def getNextWord(userWord):
    word = db.srandmember(userWord)
    return word

# --- COMMANDS ---
# A command to make the bot speak manually in the server where the command was used
# Giving arguments will make the bot complete the given sentence
@bot.command()
async def speak(ctx, arg = None):
    if arg and len(arg) <= 200:
        # User has given words to complete
        userWords = arg.split()
        lastWord = userWords[-1]
        if (lastWord == 'is' or lastWord == 'are'):
            # Combine the original user words with one word only, but with a space between
            nextWord = getNextWord(lastWord)
            if nextWord:
                sentence = f'{arg} {nextWord}'
            else:
                sentence = 'I have no idea'
        else:
            sentence = formulateSentence(userWords)
            # Combine the original user words with the formulated sentence, but with a space between
            # sentence = f'{arg} {formulatedSentence}'
    else:
        # No words given, formulate normally
        sentence = formulateSentence()
    # Send the final sentence to the server & channel where the command was used
    await ctx.send(sentence)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    game = discord.Game('¤speak')
    await bot.change_presence(activity=game)

bot.run(config.botToken)