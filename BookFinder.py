#!/usr/bin/env python

import sys
import os
import re
import praw
import ConfigParser
from goodreads import client
from amazon.api import AmazonAPI

def main():
	# Throw exception if config.ini not found in same directory
	if not os.path.exists("config.ini"):
		raise Exception("Configuration file not found.")

	# Read username, password, and API keys from config file
	config = ConfigParser.ConfigParser()
	config.read("config.ini")
	USERNAME = config.get("setup", "USERNAME")
	PASSWORD = config.get("setup", "PASSWORD")
	USER_AGENT = config.get("setup", "USER_AGENT")
	GOODREADS_KEY = config.get("setup", "GOODREADS_KEY")
	GOODREADS_SECRET = config.get("setup", "GOODREADS_SECRET")
	AMAZON_KEY = config.get("setup", "AMAZON_KEY")
	AMAZON_SECRET = config.get("setup", "AMAZON_SECRET")
	AMAZON_ASSOCIATE = config.get("setup", "AMAZON_ASSOCIATE")

	# Establish connections to Reddit, Goodreads, and Amazon
	r = praw.Reddit(USER_AGENT)
	r.login(USERNAME, PASSWORD, disable_warning=True)
	gc = client.GoodreadsClient(GOODREADS_KEY, GOODREADS_SECRET)
	amazon = AmazonAPI(AMAZON_KEY, AMAZON_SECRET, AMAZON_ASSOCIATE)

	# Comments that have already been replied to
	already_done = []

	while True:
		try:
			# Get comments where username is mentioned
			mentioned_comments = list(r.get_mentions())

			for comment in mentioned_comments:
				if comment.id not in already_done:
					response = ""

					# Split comment by lines
					lines = comment.body.split("\n")

					for line in lines:

						# Disregard empty lines (Reddit line break requires two \n's)
						if line:

							# Parse to get rid of username
							line_without_username = remove_username(line)

							# If author request, get a list of his/her titles
							if "Author:" in line_without_username:
								name = line_without_username[8:].strip()
								split_titles = find_author_in_goodreads(gc, name)
								
								if split_titles:
									response += "Here are some books by author " + name + ":\n\n"
								else: 
									response += "I couldn't find that author! :(\n\n"
							
							# Else the line itself is the list of titles
							else:
								split_titles = re.split("(\".*\")", line_without_username)
							
							# Find each title in Goodreads and Amazon and add info to response string
							for title in split_titles:
								cleaned_title = clean_title(title)
								response += find_book_in_goodreads(gc, cleaned_title)
								response += find_in_amazon(amazon, cleaned_title)
								response += "\n\n"
							
							# Add dividing line
							response += "___\n\n"
					
					# Append bot and crediting information to response's end
					response += USER_AGENT + " | " + append_suffix()
					
					# Add comment on Reddit and to done list
					print response
					# comment.reply(response)
					already_done.append(comment.id)
		except Exception as e:
			print e
			break

# Parses a line to remove username, which is the first substring of characters before a space
def remove_username(line):
	words = line.split()
	return " ".join(words[1:])

# Removes unnecessary quotes, commas, and spaces from a title
def clean_title(title):
	temp = re.sub("\"", "", title).strip()
	return re.sub("^,|,$", "", temp).strip()

# Looks the book's title up in Goodreads
def find_book_in_goodreads(gc, title):
	# Empty/only space string handling
	if not title.strip():
		return "You need to provide name/s!"
	
	try:
		books = gc.search_books(title)
		
		# Return relevant info if a match is found in top 3 Goodreads search results
		for book in books[:3]:
			if title.lower() in book.title.lower():
				return (book.title + " (" + book.publication_date[2] + ") " + 
					"by " + str(book.authors[0]) + " has an average rating of " + 
					book.average_rating + "/5 based on " + book.ratings_count + 
					" Goodreads reviews. ")
		
		return "I couldn't find reviews of that book on Goodreads, but it may be available on Amazon. "
	except Exception as e:
		print e
		return "I couldn't find reviews of that book on Goodreads, but it may be available on Amazon. "

# Looks up an author in Goodreads
def find_author_in_goodreads(gc, name):
	result = []

	# Empty/only space string handling
	if not name.strip():
		return result

	try: 
		author = gc.find_author(name)
		
		# If the author is found in Goodreads, add to result the titles of his/her top 3 books
		if author: 
			for book in author.books[:3]:
				result.append(book.title)
		
		# Returns either top 3 books' titles or empty list
		return result
	except Exception as e:
		print e
		return result

# Looks up a book in Amazon by title
def find_in_amazon(amazon, title):
	# Empty/only space string handling
	if not title.strip():
		return ""
	
	try:
		# Search Amazon's book index by title without parenthetical information that may 
		# have been added by Goodreads
		phrases = title.split(" (")
		books = amazon.search_n(1, Title=phrases[0], SearchIndex='Books')
		
		# Get the product's URL and remove the Amazon associate id, which comes after last "/"
		split_url = books[0].offer_url.split("/")
		url = "/".join(split_url[:-1])
		
		# Return URL and formatted price
		return ("[It is available on Amazon for $" + 
			str(format((books[0].price_and_currency[0]), ".2f") + "](" + url + ")."))
	except Exception as e:
		print e
		return "However, I can't seem to find it on Amazon! :("

# Returns bot and crediting information, used to add those to the end of the reply comment
def append_suffix():
	return ("This tool uses the [Goodreads](https://www.goodreads.com/api) and " +
		"[Amazon Product Advertising](https://affiliate-program.amazon.com/gp/" + 
		"advertising/api/detail/main.html) API's.")

if __name__ == '__main__':
  main()