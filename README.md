# WebScraper
This is a beginner's project that I implemented to understand the basics of web scraping. 

File kayak.py contains a class with all the functions required to scrape flights between any 2 airports. The user has to input the source and destination airports, as well as the dates that they are interested in. The class object then scrapes the corresponding flight options, processes them and stores them in a pandas dataframe. Finally, the file is exported in a .csv format. 

The whole process is encapsulated in a .run() function. The user has to only create a class object and call the .run() function.

Google Chrome browser in a Linux environment has been used for scraping, and therefore the chromedriver utility is required. Running the code on other platforms may require a different version of chromedriver to function properly.
