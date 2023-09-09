# Survey for Web Scraping Tools

The exponential growth of data in our daily lives offers businesses an opportunity to gain insights into customer behavior, market trends, and competitive intelligence.
However, collecting, organizing, and analyzing large volumes of data can be a daunting task.
Web scraping tools can help in extracting data from websites such as e-commerce, social media, and news websites.
The primary goal of this project is to survey and analyze various web scraping tools available for extracting data.
The project will evaluate the effectiveness of web scraping tools using metrics such as speed, accuracy, ease of use, cost, etc.
The project aims to provide insights into the advantages and disadvantages of using different web scraping tools, along with recommendations for the best tool for specific business needs.

In this Project we have targeted 4 different areas of data inouts. 
- Youtube
- Twitter
- Amazon
- US News

To scrape data from each of them we have established few scraping agents that are either free, open source or paid.
- Octoparse
- Scrapy
- Reaper
- BeautifulSoup
- Tweepy

To compare a fair evaluation, we have created few set of experiments and also metrics on what they are compared
- Twitter - OctoParse vs Reaper vs Twitter API (via Tweepy)
- Amazon - OctoParse vs Beautiful Soup
- US News - OctoParse vs Scrapy+Selenium
- Youtube - OctoParse vs Reaper

Metrics for Evaluation
- Performance Efficiency - Time taken to scrape same set of data, Max Limit, Fault Tolerance
- Ease of Use - Proper Documentation for libraries and tools, scraping procedure.
- API vs Non-API - Amount of Coding needed, Availability of Non-API tools
- Cost to Scrape Data -  Is the tool free to use, charges involved per API call, upper limit on amount of Data

The repository has been set up with the structure of 
- Code: All code and files that are needed for the scraping agents.
- Data: All the scraped data has been stored in this folder.
- Evaluations: Relevant evaluations are present in this folder.

To visualize the huge amount of data scraped, we also came up with a interactive dashboard which can be accessed through
[Interactive Dashboard](https://sahilvora10.github.io/Survey-for-Web-Scrapers/)

