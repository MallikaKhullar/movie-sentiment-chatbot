#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math
import string

import numpy as np
import re
from movielens import ratings
from random import randint
import random
from PorterStemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.user_vec = {}
      #get more complete list of negations
      self.negation = {'didn\'t', 'never', 'not', 'don\'t'}
      # Responses 
      self.responses = { 
        'no_movies_found': ["You didn't mention any movies. Could you suggest one?"],
        'prompt':["Tell me about another movie you have seen."],
        'like_movie':["You liked %s."],
        'dislike_movie':["You did not like %s."],
        'sentiment_clarification': ["I'm sorry, I'm not quite sure if you liked %s."],
        'movie_clarification':["Sorry, I don't understand. Tell me about a movie that you have seen."],
        'fake_movie':["I'm sorry, I don't recognize that movie. Could you tell me about a different one?"],
      }

      self.stemmedSentiment = {}
      self.p = PorterStemmer()
      self.read_data()

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = 'How can I help you?'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Have a nice day!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      response = ""
      if self.is_turbo == True:
        response = 'processed %s in creative mode!!' % input
      else:
        # Pull the movie titles from the user input
        movie_titles = self.get_movie_names(input)
        
        # Nothing found within quotations that is a movie
        if not movie_titles:
          return self.get_response("no_movies_found")
        
        # See if the movie title is in our database
        movie_name = movie_titles[0] # just use the first movie found for now
        movie_entry = self.movie_in_db(movie_name)
        if movie_entry is None:
          return self.get_response("fake_movie")

        # Associate the movie title with a sentiment score
        score = self.get_sentiment_score(input)
        self.user_vec[self.titles.index(movie_entry)] = score  # movie_id: sentiment_score
        
        # TODO: Play around with thresholds for like/dislike
        if score == 0:
          response = self.get_response("sentiment_clarification") % movie_name
        elif score > 0:
          response = self.get_response("like_movie") % movie_name
        else:
          response = self.get_response("dislike_movie") % movie_name

      # response = 'You typed the movie %s' % movie_titles[0]
      print "Movie: %s, Vector: %s" % (movie_name, self.user_vec)
      return response

    def movie_in_db(self, movie_name):
      """Returns movie entry with the movie_name in our database."""
      movie_entry = None # entry = (movie_name, genres)
      for movie in self.titles:
        # Found the movie in our movie database!
        #TODO: handle improper capitalization, some article errors, misspellings
        if re.search("(?:[Tt]he |[Aa]n? |[Ll][ea]s? |[Ee]l |[OoAa] )?" + movie_name + "(?: \(\d\d\d\d\))?", movie[0]):
          movie_entry = movie
          break
      return movie_entry

    def get_response(self, key):
      """Returns a random response for the given key."""
      return random.choice(self.responses[key])

    def get_movie_names(self, input):
      """Pulls all movie names inside quotations from the input."""
      movie_regex = r"\"((?:\w+\W*)*)\""
      return re.findall(movie_regex, input)

    def get_sentiment_score(self, input):
      """Get the sentiment score of a full phrase."""
      score = 0
      line = input.split()
      isNeg = False
      for word in line:
        print word
        if word in self.negation:
          isNeg = True
          continue
        word = self.p.stem(word)
        if word in self.sentiment:
          if (isNeg and self.sentiment[word] == 'pos') or (not isNeg and self.sentiment[word] == 'neg'):
            score -= 1
          elif (isNeg and self.sentiment[word] == 'neg') or (not isNeg and self.sentiment[word] == 'pos'):
            score += 1
          print score
          if isNeg:
          #check how we tokenize
            isNeg = False
      print score
      return score


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      # print len(self.ratings[0])
      # print len(self.ratings[1])
      self.binarize()
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)
      self.stemSentiment()

    def stemSentiment(self):
      for old_key,value in self.sentiment.iteritems():
        new_key = self.p.stem(old_key)
        self.stemmedSentiment[new_key] = value

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      for i,r in enumerate(self.ratings):
        if r > 3.0:
          self.ratings[i] = 1
        else:
          self.ratings[i] = -1


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure
      pass


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # best = -1.0
      # recommendation = []
      # for movie in self.titles:
      #   v = #row i in self.titles, self.ratings
      #   d = self.distance(u, v)
      #   if d > best:
      #     best = d
      #     recommendation = v
      #   if best == 1:
      #     break
      # return recommendation
      pass


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
