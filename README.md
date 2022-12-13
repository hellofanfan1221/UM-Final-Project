# UM SI507 Final Project

## Project goal
- Costco has its own recommendation engines. In each shopping experience on Costco’s webpage, there will be a section called “Members also bought” (refer to picture below), which recommends customers to buy similar products.
- The project aims to analyze the recommendation product data scraped from the website and find out the top k levels of recommendation for related product when a customer searched for it on Costco.
- The scraper uses BeautifulSoup and Selenium Webdriver to retrieve the following 6 fields of data from a Costco page and make it into a graph data structure

## Getting Started (Prerequisites)
- Python 3.8
- Webdriver (This project uses Chrome)
- Selenium
- BeautifulSoup
- Plotly
- change the path in function **load_driver_path()** to your own chromedriver

## Running scrape_with_cache.py
1. Run scrape_with_cache.py 
2. Users input their desired product url on Costco website to the command line input 
3. The scraper starts to retrieve recommendation products and store it in the non-directed graph
4. User input levels of recommendation
  * Enter 1 ~ k (one of the integers) to see the bar graph of prices to recommendation product regarding the level
  * Enter 0 to see the bar graph of average prices to recommendation product regarding all levels
5. The program uses Plotly to visualize the bar graph in the browser
6. Users enter exit to quit the program

