#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math

import numpy as np
import re
from movielens import ratings
from random import randint

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.user_vec = {}
      self.read_data()
      # Responses 
      self.responses = { 
        'no_movies_found': ["You didn't mention any movies. Could you suggest one?"],
        'prompt':["Tell me about another movie you have seen."],
        'like_movie':["You liked %s."],
        'dislike_movie':["You did not like %s."],
        'sentiment_clarification': ["I'm sorry, I'm not quite sure if you liked %s."],
        'movie_clarification':["Sorry, I don't understand. Tell me about a movie that you have seen."]
      }

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
        # print self.titles
        movie_regex = r"\"((?:\w+\W*)*)\""
        movie_titles = re.findall(movie_regex, input)
        movie_name = movie_titles[0]
        if not movie_titles:
          response = self.responses["no_movies_found"][0]
        else:
          movie_found = False
          for movie in self.titles:
            print movie[0]
            if movie_name == movie[0]:
              print "MOVIE FOUNDDDDDDDDDDDD"
              score = self.get_sentiment_score(input)
              print score
              self.user_vec[self.titles.index(movie)] = score
              #play around with thresholds for like/dislike
              if score == 0:
                response = self.responses["sentiment_clarification"][0] % movie_name
              elif score > 0:
                response = self.responses["like_movie"][0] % movie_name
              else:
                response = self.responses["dislike_movie"][0] % movie_name
              movie_found = True
              break
          if not movie_found:
            response = self.responses["movie_clarification"][0]
          
          #response = 'You typed the movie %s' % movie_titles[0]
          print "Movie: %s, Vector: %s" % (movie_name, self.user_vec)
      return response

    def get_sentiment_score(self, input):
      score = 0
      line = input.split()
      for word in line:
        if word in self.sentiment:
          if self.sentiment[word] == 'pos':
            score += 1
          else:
            score -= 1
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
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)


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
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

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
