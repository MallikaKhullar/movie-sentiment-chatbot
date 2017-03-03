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
      self.name = 'MovieBot'
      self.is_turbo = is_turbo
      self.spellCheck = False
      #get more complete list of negations
      self.negation = {'didn\'t', 'never', 'not', 'don\'t'}
      self.intensifiers = {'love', 'hate', 'really', 'very', 'favorite', 'amazing', 'incredible', 'best', 'worst'}
      self.yes = {'yes', 'yeah', 'ya', 'uh-huh'}
      # Responses 
      self.responses = { 
        'no_movies_found': ["Hmmm you didn't mention any movies, %s. Could you suggest one? ", "Let's get back on track, %s.",  
                          "Are you trying to distract me, %s?", "%s, I'd really appreciate it if you told me about some movies.",
                          "Let's get back on track. Movies are serious business, %s.", "Are you making fun of me, %s? ", "Frankly my dear %s, I don't give a damn.",
                          "As if, %s!", "That'll do, %s. That'll do.", "You talkin' to me? %s?", "Hey, %s, I'm walking [aka trying to talk about movies] here!"],
        'prompt':["Tell me about another movie! ", "Could you tell me about another movie? ", "What other movies have you liked/disliked? ", 
                "Just a couple more, and I'll find the perfect movie for you :)", "Throw me another one!", "Another?", "Tell me more! Tell me more! (like does he have a car?)"],
        'like_movie':["You liked %s. ", "Yesss, more love for %s! ", "So you liked %s, huh? ", "Haha yeah %s was awesome! ", "SAME %s is my favorite movie! ", "LOVE IT. %s is great. ",
                      "%s is my favorite! ", "Don't hate me, but I actually wasn't a huge fan of %s :/ Totally fine though. ", 
                      "You've got great taste in movies if you liked %s. I'll have what you're having! "],
        'dislike_movie':["Oh no, I loved %s! Are you sure we're friends? ", "Yeah, I actually wasn't a huge fan of %s either. ", "Inconceivable! Everyone likes %s!"
                      "Don't be a hater! Someone's sister worked really hard on %s! ", "It makes me really sad when people don't like movies. Especially classics like %s. ",
                       "All movies deserve love, even %s :( ", "Don't be so negative, real-life people worked really hard on %s. ", "*sniff* Why can't we all just get along? You, me, and %s? "],
        'sentiment_clarification': ["I'm sorry, I'm not quite sure if you liked %s. ", "Oops, not sure if I understood right. Did you like %s?", 
                              "Sorry, did you like or dislike %s?", "Okay, great! And did you like %s or not?", "Sorry, I can't tell if you liked %s or not... did you?"],
        'movie_clarification':["Sorry, I don't understand. Maybe try re-entering the movie? ", "I'm not quite sure if I got it. Could you try again with the full title?", 
                              "Hmm still not quite sure what you mean. Try the full title again? "],
        'fake_movie':["I'm so sorry, I've never seen that movie! Could you tell me about a different one? ", "Are you sure that's a real movie? "
                  "This is so embarrassing. I've actually never seen that one :/ ", "Haha are you trying to trick me? ", 
                  "Don't hate me, but I don't know that one... Try another? ", "Houston, we have a problem. I've never heard of that movie! "],
        'too_many_movies':["That's a little too much at once! How about you tell me about them one at a time?", 
                      "Sorry, I can only process one movie at a time. ", "Whoa whoa whoa slow down there! One at a time please :)"],
        'multiple_matches':["I found a couple movies, but I'm not sure which one you mean! They are: %s \n\tWhich one did you want to tell me about?",
                            "You've got some options! Here they are: %s \n\tWhich one did you want to tell me about?", 
                            "Okay I've got a couple of titles that match that: %s \n\tTell me which one!", "You've got choices! They are: %s\n\tWhich one did you mean?"],
        'recommend':["I know one I think you'd like, %s! You should check out %s. ", "%s, I think you would enjoy %s. ", 
                    "%s. Have you ever seen %s? It seems right up your alley! ", "%s, you HAVE to see %s. ", "Elementary, my dear %s. You should watch %s! ", 
                    "Hey %s, here's an 'offer you can't refuse'! You should watch %s! "]
      }
      self.reference_regex = "(?:that (?:movie|one)?|it)"
      self.stemmedSentiment = {}
      self.p = PorterStemmer()
      self.read_data()
      self.user_vec = collections.defaultdict(lambda: 0)
      #constant value for how many data points needed for a recommendation
      self.threshold = 5
      #constant value for number of movies to recommend
      self.k = 1
      self.recommendations = [(0,0)] * len(self.ratings)
      self.spell_threshold = 4 # max valid edit distance
      #list containing memory of previous interaction
      self.memory = []
      self.user_name = ""

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Hey! I\'m %s and I\'m here to help you find some good movies. For starters, could you tell me your name? \n\tJust your first name is fine, I like to keep it casual :)" % self.name

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Bye bye now! Have fun storming the castle!'

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

      print "memory: %s" % self.memory

      # Set the user name if not yet set!
      if self.user_name == "":
        return self.set_name(input)

      response = ""
      movie_titles = []
      if self.is_turbo == True:
        response = 'processed %s in creative mode!!' % input
      else:
        ###### Pull the movie titles from the user input ######
        movie_titles = self.get_movie_names(input)
        print "movie_titles: " % movie_titles
        if self.spellCheck:
          m = self.memory[1]
          self.memory = [self.memory[0]]
          if input.lower() in self.yes:
            movie_titles.append(self.titles[m][0])
          else:
            return self.get_response("movie_clarification")

        #if list of movies in memory: disambiguating a sentence
        elif len(self.memory) > 2:
          movie_titles = self.disambiguate(input)
          self.memory = [self.memory[0]] #clear candidate movies from memory, keep sentiment sentence
          if len(movie_titles) > 1:
            return self.get_response("movie_clarification")

        # Nothing found within quotations that is a movie
        elif not movie_titles:
          #check for reference to previous movie
          if len(self.memory) > 1: #changed from elif
            m = self.titles[self.memory[1]][0] #most recently-mentioned movie
            movie_titles.append(m)
            if 'yes' in input.lower():
              self.memory[0] = "like"
            elif 'no' in input:
              self.memory[0] = "dislike"
            else:
              self.memory[0] = input
            print "memory: %s" % self.memory
          #modifying earlier sentiment. potential issue--only works once
          else:
            if re.search(self.reference_regex, input): 
              movie_titles = self.get_movie_names(self.memory[0]) #get movie from previous exchange
            if not movie_titles: #still no movies found in memory!
              return self.get_response("no_movies_found") % self.user_name
            self.memory = [input] #use most recent input for sentiment
        # Place phrase with movie into memory
        else:
          self.memory = [input]
          print "memory: %s" % self.memory
        
        ###### See if the movie title is in our database ######

        # Get a single movie from the user input
        if len(movie_titles) > 1:
          return self.get_response("too_many_movies")
        
        movie_name = movie_titles[0] # just use the first inputted movie for now
        
        # Get the full movie entry (with genre) from our database
        movie_entry = self.movie_in_db(movie_name)
        print "movie_in_db returned: %s" % movie_entry
        if len(movie_entry) == 0:
          # Try to spell check 'movie_name'
          candidate_string, spell_score = self.bestSpellCandidate(movie_name)
          if spell_score <= self.spell_threshold:
            movie_entry = self.movie_in_db(candidate_string)
            if movie_entry:
              self.spellCheck = True
              self.memory = [self.memory[0], movie_entry[0]]
              return "Did you mean %s?" % self.colloquialize(self.titles[movie_entry[0]][0])
            #TODO: confirm movie is the spell checked word!
            # return self.get_response("clarify_movie")
          else:  #not a real movie!
            return self.get_response("fake_movie")

        # Found ~multiple~ movie matches in the database
        if len(movie_entry) > 1:
          response = self.get_response("multiple_matches")
          options = ""
          for i, m in enumerate(movie_entry):
            options += "\n\t\t- " + self.titles[m][0]
            #options += "\n\t\t%d) " % (i+1) + self.titles[m][0]
          self.memory += movie_entry
          print "memory: %s" % self.memory
          return response % options

        ###### Associate the movie title with a sentiment score ######

        score = self.get_sentiment_score(self.memory[0])
        # self.user_vec[movie_entry[0]] = score - (score - 1) # movie_id -> binarized sentiment score
        self.user_vec[movie_entry[0]] = score # movie_id -> binarized sentiment score
        print "score: %d, uservec score: %d" % (score, self.user_vec[movie_entry[0]])
        
        movie_name = self.colloquialize(self.titles[movie_entry[0]][0]) #fix ", The" endings
        if score == 0:
          self.memory.append(movie_entry[0])
          print "memory: %s" % self.memory
          response = self.get_response("sentiment_clarification") % movie_name
        else:
          if score > 0:
            response = self.get_response("like_movie") % movie_name
          else:
            response = self.get_response("dislike_movie") % movie_name
          response += self.get_response("prompt")

      # Check if user has rated more movies than the threshold
      if len(self.user_vec) > self.threshold:
        recommendations = self.recommend(self.user_vec) # only calculate recommedations when about to make a recommendation
        response = self.get_response("recommend") % (self.user_name, self.colloquialize(recommendations[0][0])) # title information
        response += " It's a " + re.sub("\|", "and ", recommendations[0][1]).lower() + "!"                   # genre information

      print "USER VEC: %s" % self.user_vec
      return response

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def disambiguate(self, input):
      movie_titles = []
      for i in range(1, len(self.memory)): #first index is user input
        m = self.titles[self.memory[i]][0]
        input = re.sub("[^A-Za-z0-9 ]", "", input) #test
        print "input: %s m: %s" % (input, m)
        if re.search(input.lower(), m.lower()): #handle capitalization errors
          movie_titles.append(m) #make that movie the current movie title (maybe fix later, too general)
          print "movie titles : %s" % movie_titles
          #break
      return movie_titles

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
      print "full movie entry = %s" % movie_entry
      #check for extraneous findings (if full match)
      if len(movie_entry) > 1:
        temp = []
        for m in movie_entry:
          current = self.colloquialize(self.titles[m][0]).strip()
          target = re.sub("\([^\)]*\)", "", movie_name).strip() + '$' #remove info in parentheses to match colloquial version
          print "current: %s, target: %s" % (target.lower(), current.lower())
          if re.match(target.lower(), current.lower()):
            print "Full match! %s" % self.titles[m][0]
            temp.append(m)
        print "temp: %s" % temp
        if len(temp) > 0:
          movie_entry = temp
      "returning %s" % movie_entry
      return movie_entry

    def bestSpellCandidate(self, input_movie):
      #TODO: make sure that the edit is at start of movie title (bug--"bpys" matched "bad boys" not "boys")
      input_movie = input_movie.lower().strip()
      best_title = ""
      best_edit_distance = float("inf")
      for title in self.title_names:
        title = re.sub("\([^\)]+\)", "", title).lower().strip() #remove year and lowercase (same as colloquialize function!)
        if ", the" in title:
          title = "the " + re.sub(", the", "", title) # remove ", the" to the front
        edit_distance = self.editDistance(input_movie, title, len(input_movie), len(title), 0)
        # print input_movie, title, edit_distance
        if edit_distance < best_edit_distance: #search for minimum edit distance
          best_title = title
          best_edit_distance = edit_distance
      return best_title, best_edit_distance

    def editDistance(self, s1, s2, m, n, level):
      """Calculates the edit distance between strings"""
      # Optimize: Exit Early!
      if level >= self.spell_threshold:
        return min(m, n)

      # Base Case: Empty string, remove all characters of other string
      if m == 0:
          return n
      if n == 0:
        return m

      # Recursive Case: Calculate Edit Distance
      if s1[m-1] == s2[n-1]:    #characters are same
        return self.editDistance(s1, s2, m-1, n-1, level+1)
      else:                     #last characters are not same
        return 1 + min(self.editDistance(s1, s2, m,   n-1, level+1),      # insert
                       self.editDistance(s1, s2, m-1, n,   level+1),      # deletion
                       self.editDistance(s1, s2, m-1, n-1, level+1)     # substitution.
                       )

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
      weight = 1.0
      line = re.sub("\"[^\"]+\"", "", input)
      if re.search("!+", line):
        weight += .5
      line = line.split()
      isNeg = False
      for word in line:
        if word in self.negation:
          isNeg = True
          continue
        word = self.p.stem(word)
        if word in self.intensifiers:
          weight += 0.5
        if word in self.stemmedSentiment:
          if (isNeg and self.stemmedSentiment[word] == 'pos') or (not isNeg and self.stemmedSentiment[word] == 'neg'):
            score -= 1
          elif (isNeg and self.stemmedSentiment[word] == 'neg') or (not isNeg and self.stemmedSentiment[word] == 'pos'):
            score += 1
          if isNeg:
          #TODO check how we tokenize
            isNeg = False
      if score > 0:
        score = weight
      if score < 0:
        score = (-1) * weight
      print "Sentiment score: %d" % score
      return score

    def colloquialize(self, title):
      """Moves the ", The" to the front of a movie title"""
      title = re.sub("\([^\)]+\)", "", title) #gets rid of year
      if ", The" in title:
        title = "The " + re.sub(", The", "", title)
      return title.strip()

    def set_name(self, input):
      """Sets the user name"""
      self.user_name = input
      return "Hey, %s! Nice to meet you! Now that we've ~hit it off~, why don't you tell me about a movie you've seen?" % self.user_name

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      self.title_names = [title for title, genre in self.titles]
      self.title_genres = [genre for title, genre in self.titles]
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
      # self.ratings[i][np.where(user_ratings>3.0)] = 1
      # self.ratings[i][np.where(user_ratings>0.0)] = -1
      # self.ratings[i][np.where(user_ratings==0.0)] = 0  

    def distance(self, u, v):
      """Calculates the cosine distance function between vectors u and v"""
      # Note: you can also think of this as computing a similarity measure
      a = np.array(u)
      b = np.array(v)
      return np.dot(a, b)/((np.linalg.norm(a)*np.linalg.norm(b))+1e-7)

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering and a content-based system"""
      
      # Calculate the input vector similarity against all other movies.
      for i in u: # each movie suggestion in user input {232: 1, 423:-1}
        for j, movie_user_ratings in enumerate(self.ratings): 
          if i != j:
            # Calculate item-item collaborative filtering similarity
            collab_similarity = self.distance(self.ratings[:,i], self.ratings[:,j]) #item-item similarity: dot product of movie i and movie j
            # print "movie %s,%s collab_similarity = %s" % (i,j,collab_similarity)

            # Calculate the content-based similarity
            input_genre = self.title_genres[i].split("|")
            movie_genre = self.title_genres[j].split("|")

            # Genre characteristics
            num_shared_genre = len(set(input_genre) & set(movie_genre))
            input_length = len(input_genre)
            movie_length = len(movie_genre)

            content_similarity = num_shared_genre/(math.sqrt(input_length)*math.sqrt(movie_length))
            # print "movie %s,%s content_similarity = %s" % (i,j,content_similarity)
            # print "-------------------"

            # Calculate the weighted similarity
            alpha = 0.6
            weighted_similarity = (1-alpha)*collab_similarity + (alpha)*content_similarity

            # Update the weighted score for each user!
            user_score = self.recommendations[j][0] + weighted_similarity * u[i] #multiply by user's rating for movie i
            self.recommendations[j] = (user_score, j)
      
      sortedScores = sorted(self.recommendations, key=lambda tup: tup[0], reverse=True) #sort by score
      # for score in sortedScores:
      #   print score

      recommendations = []
      #return list of k movie titles
      for i in range(0, self.k):
        recommendations.append(self.titles[sortedScores[i][1]])
            
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
      This is MovieBot! She's a total movie buff, and loves giving putting her encyclopedic
      knowledge of all things cinematic to good use.  She loves all movies equally and 
      gets sad if people don't like them, so be nice! 
      Please put movie titles in quotes, and say how you feel about the movie. After about %d
      suggestions, Moviebot will give you her expert advice!
      """ % self.threshold


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
