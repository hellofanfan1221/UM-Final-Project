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

## How recommendation products are stored into graphs
In this project, I stored the dependency of the recommendation data into a non-directed graph using defaultdict(list). Every node of the graph is the url of the recommendation product on Costco. The user will select one product on Costco website, then the scraper retrieves the recommendation products data in the “Member also bought” section, and then the recommendation products will be the first level from the root node, which is the product selected by the user at first. Similarly, the scraper will then put the recommendation products’ url into URL, then continue scraping the following levels of recommendation. The graph is completely constructed after all recommendation product are reached (I used productCache.json to check the repeated products). The graph is stored in recommendation_product_graph.json.
