# book-finder

Reddit bot that, when called upon by a mention, searches for book/s on Amazon and Goodreads. Replies with a comment containing reviews and publication information from Goodreads, along with a link to the best result for the book on Amazon. Can also be called for an author, returning the author's top 3 books with relevant information from Goodreads and link to Amazon. 

Has ability to take multiple books at a time, separated by commas. Book titles with commas in them should be enclosed in quotes, bot can parse and figure out the titles. Also has ability to handle multi-line requests, including both book and author requests in one comment. 

Demo of full capabilities: 

![ScreenShot](https://raw.github.com/rodhoopar/book-finder/master/book%20finder%20example.png)

Utilizes the Goodreads and Amazon Product Advertising API's. Needs developer keys from both and an Amazon affiliate account to use. Inspired by u/yoalan's bot for Netflix. 
