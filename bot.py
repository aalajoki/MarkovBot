# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import pickle
import re
from random import randint
import redis
# Contains the list of censored words, the max word and sentence length and the discord bot token
import config

db = redis.Redis(host='localhost', port=6379, charset="utf-8", decode_responses=True)

description = "A silly bot that pretends to learn to speak."
bot = commands.Bot(command_prefix="¤", description=description)

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
def formulateSentence():
    sentence = ''
    firstWord = db.srandmember('FirstWords')
    sentence += firstWord
    sentenceLength = 1

    previousWord = firstWord

    while True:
        nextWord = db.srandmember(previousWord)

        if (nextWord == 'ENDSENTENCE'):
            return sentence
        else:
            sentence += ' ' + nextWord
            previousWord = nextWord
            sentenceLength += 1
            if (sentenceLength >= config.maxSentenceLength):
                return sentence

# --- COMMANDS ---
# A command to make the bot speak manually in the server where the command was used
@bot.command()
async def speak(ctx):
    sentence = formulateSentence()
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