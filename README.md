# Premier-League-Match-Predictor
This is a model that predicts the outcomes of Premier League matches using a deep neural network, and a dataset containing data from the last 11 years of football (scraped from various websites). When trained on the 2012/13 - 2021/22 seasons, and then tested on the most recent season 2022/23, the model predicted outcomes (Home Win, Away Win, Draw) with 57% accuracy. When betting odds were added to create a betting-recommendation system, the model's recommendations returned 17% (annualized), far more than the SnP 500 in the same timeframe.

Contained within the repository are 4 subfolders:

The Data subfolder contains Excel and Json files that are produced by running the web scraping programs

The Web Scraping Code subfolder contains the code that produces the aforementioned data by using selenium to scrape various websites. Note, this code takes a very long time to run due to the vast amount of data being collected and the complexity of the scraped websites. Overall, all the progams take around ~8 hours to run. However, you can run them and watch what happens then terminate them after you have seen enough (the repo comes with the final data anyway so there is no need for you to perform any of the scraping). Note, the code for these scrapers contains print statements that help you see how far along the scraping is.

The Data Processing and Model Training Code prepares the scraped data for the neural network, and also adds additional features (form-based features for both the home and away teams) that are calculated using scraped features. This doesn't take too long and can be run.

The Flask App folder contains the code for a flask app that I am currently building. Once it is finished, I will host it on the cloud, but for the time being, you can run it on your own computer.

If you were to run all the code from scratch having deleted the data files, the order of code to be run would be:

PL_website_webscraper.py,   transfermarkt_scraper.py,  whoscored_scraper.py,  starting_xi_scraper.py,  analysis of scraped data.py,  model.py,  Betting outcomes for last season.py

The initial data is scraped by PL_website_webscraper.py, which creates a table where each row corresponds to a single match, and has columns for the season, date, home team, away team, and score. The result of this scraping is added to by whoscored_scraper.py, which adds advanced team metrics. Transfermarkt_scraper.py and starting_xi_scraper.py run independently of the aforementioned scrapers, and produce a json containing transfer values of players over the years and an excel file of starting xis in each game respectively. The results of who_scored_scraper.py, transfermarkt_scraper.py, and starting_xi_scraper.py are combined to create a final dataset via analysis of scraped data.py, which also adds additional form-based features that can be inferred from the scraped features.

Finally, this data is used to train and test a neural network in model.py (trained on data from 2012/13 - 2021/22 seasons and tested on the 2022/23 season), which currently contains 6 layers and uses a softmax activation function to output the probabilities of a home win, an away win, and a draw for each game from the testing season. These probabilities can be used either to make definitive predictions (highest probability -> predicted outcome), and can also be combined with betting odds to determine whether betting on a home win, away win, draw (or not betting at all) has the highest expected value and is therefore the best course of action. This is done in Betting outcomes for last season.py.

Finally, the Flask app can be run to check out the interactive app that I am currently building to display the results of the model.

for a more detail, check out comments in individual files. However, given the nature of this program, the best way to see and understand how the data is scraped is to run the code and watch the data being scraped.

Lastly, here is a key for some of the abbreviations used in the data:

GFPG - Goals For Per Game,   GAPG - Goals Against Per Game

