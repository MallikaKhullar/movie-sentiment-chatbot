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
import collections

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      #get more complete list of negations
      self.negation = {'didn\'t', 'never', 'not', 'don\'t'}
      # Responses 
      self.responses = { 
        'no_movies_found': ["You didn't mention any movies. Could you suggest one? "],
        'prompt':["Tell me about another movie you have seen. ", "Could you tell me about another movie? "],
        'like_movie':["You liked %s. ", "So you liked %s, huh? "],
        'dislike_movie':["You did not like %s. ", "Yeah, I wasn't a huge fan of %s either. "],
        'sentiment_clarification': ["I'm sorry, I'm not quite sure if you liked %s. "],
        'movie_clarification':["Sorry, I don't understand. Tell me about a movie that you have seen. "],
        'fake_movie':["I'm sorry, I don't recognize that movie. Could you tell me about a different one? "],
        'too_many_movies':["That's a little too much at once! How about you tell me about them one at a time?", 
                      "Sorry, I can only process one movie at a time."],
        'multiple_matches':["I found a couple movies, but I'm not sure which one you mean! They are: %s \n\tWhich one did you want to tell me about?"],
        'recommend':["I know one I think you'd like! You should check out %s. ", "I think you would enjoy %s. ", 
                    "Have you ever seen %s? It seems right up your alley! "]
      }

      self.stemmedSentiment = {}
      self.p = PorterStemmer()
      self.read_data()
      #self.user_vec = [0] * len(self.ratings[0])
      self.user_vec = collections.defaultdict(lambda: 0)
      #constant value for how many data points needed for a recommendation
      self.threshold = 1
      #constant value for number of movies to recommend
      self.k = 1
      self.recommendations = [[0, 0]] * len(self.ratings[0])
      #list containing memory of previous interaction
      self.memory = []

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
      movie_titles = []
      if self.is_turbo == True:
        response = 'processed %s in creative mode!!' % input
      else:
        # Pull the movie titles from the user input
        movie_titles = self.get_movie_names(input)
        
        # Nothing found within quotations that is a movie
        if not movie_titles:
          #if list of movies in memory: disambiguating a sentence
          if len(self.memory) > 2:
            for i in range(1, len(self.memory)): #first index is user input
              m = self.titles[self.memory[i]][0]
              if re.search(input.lower(), m.lower()): #handle capitalization errors
                movie_titles.append(m) #make that movie the current movie title (maybe fix later, too general)
                print "movie titles : %s" % movie_titles
                break
          #check for reference to previous movie
          elif len(self.memory) > 1:
            m = self.titles[self.memory[1]][0] #most recently-mentioned movie
            movie_titles.append(m)
            self.memory[0] = input
          else:
            print ""
            #check for movie title without quotes
          if not movie_titles:
            return self.get_response("no_movies_found")
        else:
          self.memory = [input]
        
        if len(movie_titles) > 1:
          return self.get_response("too_many_movies")
        
        # See if the movie title is in our database
        movie_name = movie_titles[0] # just use the first movie found for now
        movie_entry = self.movie_in_db(movie_name)
        print "movie_in_db returned: %s" % movie_entry
        if len(movie_entry) == 0:
          return self.get_response("fake_movie")

        if len(movie_entry) > 1:
          response = self.get_response("multiple_matches")
          options = ""
          for i, m in enumerate(movie_entry):
            options += "\n\t\t%d) " % (i+1) + self.colloquialize(self.titles[m][0])
          self.memory += movie_entry
          return response % options

        # Associate the movie title with a sentiment score
        score = self.get_sentiment_score(self.memory[0])
        self.user_vec[movie_entry[0]] = score - (score - 1) # movie_id -> binarized sentiment score
        print "score: %d, uservec score: %d" % (score, self.user_vec[movie_entry[0]])
        
        #standardize movie titles
        movie_name = self.colloquialize(self.titles[movie_entry[0]][0])
        if score == 0:
          self.memory.append(movie_entry[0])
          response = self.get_response("sentiment_clarification") % movie_name
        else:
          if score > 0:
            response = self.get_response("like_movie") % movie_name
          else:
            response = self.get_response("dislike_movie") % movie_name
          response += self.get_response("prompt")

      if len(self.user_vec) > self.threshold:
        recommendations = self.recommend(self.user_vec) # only calculate recommedations when about to make a recommendation
        response += self.get_response("recommend") % self.colloquialize(recommendations[0][0])
        response += " It's a " + re.sub("\|", " and a ", recommendations[0][1]).lower() + "!"

      print "USER VEC: %s" % self.user_vec
      return response

    def movie_in_db(self, movie_name):
      """Returns movie entry with the movie_name in our database."""
      movie_entry = []
      movie_name = re.sub("[\(\)]", ".", movie_name) #replace parentheses with "." to avoid bugs in regex
      movie_name = "^" + re.sub("^(?:[Tt]he |[Aa]n? |[Ll][eao]s? |[Ee]l |[OoAa] )", "(?:\w+\W+)?", movie_name) #allow for misuse of articles
      print "movie name: %s" % movie_name
      for i, movie in enumerate(self.titles):
        # Found the movie in our movie database!
        if re.search(movie_name.lower(), movie[0].lower()): #handle improper capitalizations
          movie_entry.append(i)
          print "appending %s" % movie[0]
      print "movie entry = %s" % movie_entry
      return movie_entry

    def get_response(self, key):
      """Returns a random response for the given key."""
      return random.choice(self.responses[key])

    def get_movie_names(self, input):
      """Pulls all movie names inside quotations from the input."""
      movie_regex = r"\"([^\"]+)\""
      return re.findall(movie_regex, input)

    def get_sentiment_score(self, input):
      """Get the sentiment score of a full phrase."""
      print input
      score = 0
      line = re.sub("\"[^\"]+\"", "", input)
      line = line.split()
      isNeg = False
      for word in line:
        if word in self.negation:
          isNeg = True
          continue
        word = self.p.stem(word)
        if word in self.stemmedSentiment:
          if (isNeg and self.stemmedSentiment[word] == 'pos') or (not isNeg and self.stemmedSentiment[word] == 'neg'):
            score -= 1
          elif (isNeg and self.stemmedSentiment[word] == 'neg') or (not isNeg and self.stemmedSentiment[word] == 'pos'):
            score += 1
          if isNeg:
          #check how we tokenize
            isNeg = False
      return score


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def colloquialize(self, title):
      title = re.sub("\([^\)]+\)", "", title) #gets rid of year
      if ", The" in title:
        title = "The " + re.sub(", The", "", title)
      return title.strip()


    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      self.title_names = [title for title, genre in self.titles]
      self.binarize() # binarizes the ratings
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)
      self.stemSentiment()

    def stemSentiment(self):
      for old_key,value in self.sentiment.iteritems():
        new_key = self.p.stem(old_key)
        self.stemmedSentiment[new_key] = value

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      for i,user_ratings in enumerate(self.ratings):
        # Loop through each list of ratings for a given movie
        for j,movie_rating in enumerate(user_ratings):
          if movie_rating > 3.0:
            self.ratings[i][j] = 1
          elif movie_rating > 0:
            self.ratings[i][j] = -1
          else:
            self.ratings[i][j] = 0

    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # Note: you can also think of this as computing a similarity measure
      dp = 0
      for a, b in zip(u, v):
        dp += a * b
      return dp

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      
      
      # Calculate the input vector similarity against all other movies.
      for i in u:
        for j, user_ratings in enumerate(self.ratings):
          if i != j:
            similarity = self.distance(self.ratings[:,i], self.ratings[:,j]) #item-item similarity: dot product of movie i and movie j
            self.recommendations[j][0] += similarity * u[i] #multiply by user's rating for movie i
            self.recommendations[j][1] = j 
      sortedScores = sorted(self.recommendations, reverse=True)
      recommendations = []
      #return list of k movie titles
      for i in range(0, self.k):
        recommendations.append(self.titles[sortedScores[i][1]])
      """
      # Keep track of similarity and users.
      bestSimilarity = -1.0
      bestUser = 0
      for i, user_ratings in enumerate(self.ratings):
        similarity = self.distance(u, user_ratings)
        if similarity > bestSimilarity:
          bestSimilarity = similarity
          bestUser = i     
      # Recommend the movies that are not currently liked by input vector.
      recommendations = []
      bestUser_ratings = self.ratings[bestUser]
      for i, input_rating in enumerate(u):
        if input_rating == 0 and bestUser_ratings[i] != 0:
          recommendations.append(self.title_names[i])
      """
      
      return recommendations

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
