reddit_scraper.py scrapes political posts across a range of general and ideological subreddits.
Important:
Political biases are not pulled in the scraper process, that step comes later with semi_supervised_learning.py
plot_keywords.py shows the most popular keywords within the entire reddit data file.
semi_supervised_learning.py will insert a bias column into the file you choose to replace within the script
bias_plot_fact_check.py creates graphs that show the biases and their post metrics

additional files:
plot_fact_check.py is an old file that plots the total posts, popular posts, fact checked posts, and popular fact checked posts. 
    still can be used to get a general sense across general and ideological politics since bias_plot_fact_check.py splits general and ideoligical into two seperate graphs.
unsupervised_learning.py: old fact checking method I tried to implement but did not work