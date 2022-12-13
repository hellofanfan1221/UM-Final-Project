from bs4 import BeautifulSoup, NavigableString #extract the html from the request
from selenium import webdriver #deal with the dynamic javascript
from collections import defaultdict, deque
from multiprocessing import Process
import csv
import json
import time

import plotly.graph_objs as go

#########################################
############### Scraping ################
#########################################

# URLs of the specific products
URLS = deque()

# Cache functions. Called wherever needed.
CACHE_FILENAME = 'productCache.json'

# Graph for bfs
GRAPH_FILENAME = 'recommendation_product_graph.json'

# Graph for finding recommendation levels
recommendation_graph = defaultdict(list)
recommendation_level_details = defaultdict(list)

#Load the path of the driver for use
def load_driver_path():
    path = "/usr/local/bin/chromedriver"
    return path

#Loads all the urls from the URLS.txt file and appends them to the array of urls
def load_urls_from_text_file():
    urls_file = open('URLS_for_recommendation.txt', 'r')
    urls = urls_file.readlines()
    for url in urls:
        URLS.append(url.strip())
    urls_file.close()

# User input product url in command line at the beginning
def user_input_product_url():
    url = input("Input your desired product url from Costco: ")
    URLS.append(url)

#Establish the webdriver
def link_driver(path_to_driver):
    driver = webdriver.Chrome(path_to_driver)
    return driver

#  1. Loads the html data
#  2. Turns it into soup
def load_data(webdriver):
    field_names = ["Meta tags", "Name", "Description", "Category", "Price", "Image"]
    output_data = open('OutputData_for_recommendation.csv', 'a')
    writer = csv.DictWriter(output_data, fieldnames=field_names)
    writer.writeheader()

    cache_dict = open_cache()
    # for url in URLS:
    while URLS:
        url = URLS.popleft()
        # Check if URL exists in cache
        if url in cache_dict.keys():
            print("Using Cache")
        else:
            print("Fetching")
            # Get the contents of the URL
            webdriver.get(url)

            #returns the inner HTML as a string
            innerHTML = webdriver.page_source

            #turns the html into an object to use with BeautifulSoup library
            soup = BeautifulSoup(innerHTML, "html.parser")

            # write data into csv and save the dict into cache
            collected_data = extract_data(writer, soup)
            cache_dict[url] = collected_data
            # save_cache(cache_dict)

            # write data into graph
            recommended_product_urls_list = get_recommended_product_urls(soup)
            recommendation_graph[url].extend(recommended_product_urls_list)

    # print(recommendation_graph)
    dump_json_graph = json.dumps(recommendation_graph)
    fw = open(GRAPH_FILENAME, 'w')
    fw.write(dump_json_graph)
    fw.close()

    # add bfs to find levels of recommendation product
    find_recommendation_levels(cache_dict)
    # print(len(recommendation_level_details))
    # print(len(recommendation_level_details[1]))
    # print(recommendation_level_details[1])

    show_plots()
    output_data.close()

#closes the driver
def quit_driver(webdriver):
    webdriver.close()
    webdriver.quit()

## Now need to get the following from the page:
#    1. seo meta tags
#    2. product name
#    3. product description
#    4. category
#    5. price
#    6. embedded images

# gets the seo meta tags
def get_meta_tags(soup):
    meta_tags = [tags.get('name') + " is " + tags.get('content') for tags in soup.find_all('meta')[4:9]]
    # print("meta_tags")
    # print(meta_tags)
    return meta_tags

# gets the product name
def get_product_name(soup):
    product_name = soup.find('meta', property="og:description").get('content')
    # print("product_name")
    # print(product_name)
    return product_name

# logic for getting product description
def get_product_info(types, soup):
    if types == "description":
        tags = soup.find('div', class_ = "product-info-description").descendants
    elif types == "specification":
        tags = soup.find('div', id = "pdp-accordion-collapse-2").descendants
    else:
        return "Wrong String!"

    data = ""

    for tag in tags:
        if type(tag) is NavigableString and tag.string is not None:
            if(types == "description"):
                data += tag.string + "\n"
            else:
                data += tag.string
        else:
            continue

    return "\"" + data.replace("\"", "\"\"") + "\""

# gets the product description
def get_product_description(soup):
    # print("description")
    # print(get_product_info("description", soup))
    return get_product_info("description", soup)

# gets the product category
def get_category(soup):
    tags = soup.find('ul', id = "crumbs_ul")
    data = tags.contents[-2].text
    # print("data")
    # print(data.split("\n"))
    # print("catagory")
    category = ""
    for x in data.split("\n"):
        if x.strip() != "" and "Go to" not in x.strip():
            if category == "":
                category += x.strip()
            else:
                category += "/" + x.strip()
    # print(category)
    return category

# gets the product price
def get_price(soup):
    tag = soup.find('span', class_ = "value")
    # print("price")
    # print(tag.text)
    try:
        float(tag.text)
    except ValueError:
        return "29.99"
    return tag.text

# gets the product image
def get_embedded_images(soup):
    tag = soup.find('img', id = "productImage")
    return tag['src']

# Load data to csv
def extract_data(writer, soup):
    collected_data = [
        {
            "Meta tags": get_meta_tags(soup),
            "Name": get_product_name(soup),
            "Description": get_product_description(soup),
            "Category": get_category(soup),
            "Price": get_price(soup),
            "Image": get_embedded_images(soup)
        }
    ]

    for item_property_dict in collected_data:
        writer.writerow(item_property_dict)

    # output_data.close()
    return collected_data

# get recommended product urls
def get_recommended_product_urls(soup):
    tag = soup.find_all('div', class_ = "hl-product thumbnail slick-active")
    # print("tag")
    ret = []
    for single_tag in tag:
        href = single_tag.find("a").get("href")
        # print("href")
        # print(href)
        URLS.append(href)
        ret.append(href)
        # URLS_temp.add(href)
    # print(len(URLS))
    return ret

#  1. Links the driver
#  2. Loads the html data
#  3. Turns it into soup
#  4. extracts product details and loads it to csv file, and store into graph data structure
def run():
    user_input_product_url()
    path = load_driver_path()
    driver = link_driver(path)

    load_data(driver)
    # quit_driver(driver)

#########################################
############### Caching #################
#########################################

# Open the cache file or create a new cache dictionary
def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        # cache_file = open(CACHE_FILENAME, 'a')
        cache_content = cache_file.read()
        cache_dict = json.loads(cache_content)
        cache_file.close()
    except:
        cache_dict = {}
    
    return cache_dict

# Save cache dictionary to the cache file
def save_cache(cache_dict):
    dump_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, 'w')
    fw.write(dump_json_cache)
    fw.close()

# If URL in cache, retrieve the corresponding values from cache. Otherwise, connect to API again and retrieve from API.
def request_with_cache(url):
    cache_dict = open_cache()
    if url in cache_dict.keys():
        print("Using Cache")
        response = cache_dict[url]
    else:
        print("Fetching")
        response = requests.get(url).text # need to append .text, otherwise, can't save a Response object to dict
        cache_dict[url] = response # save all the text on the webpage as strings to cache_dict
        save_cache(cache_dict)
    return response



#########################################
############ Data Processing #1##########
#########################################

# Using graph data structure to analyze the top k level of 
# recommendation for related product from Costco when a customer 
# searched for the product.
def find_recommendation_levels(cache_dict):
    visited = set()
    q = deque()
    urls_file = open('URLS_for_recommendation.txt', 'r')
    urls = urls_file.readlines()
    for url in urls:
        q.append((url.strip(), 0)) # (url, level)
    urls_file.close()
    
    # execute bfs to find levels
    while q:
        curr_url, curr_level = q.popleft()
        for single_url in recommendation_graph[curr_url]:
            if single_url not in visited:
                visited.add(single_url)
                recommendation_level_details[curr_level+1].append(cache_dict[single_url])
                q.append((single_url, curr_level+1))

# show plot using Plotly
def show_plots():
    level_length = len(recommendation_level_details)
    while True:
        try:
            i = input(F"Enter levels of recommendation (from 1 ~ {level_length}) you want to see, or enter 0 to see all levels of recommendation, or enter exit to quit: ")
        except EOFError:
            return
        if i.isnumeric() and 1 <= int(i) <= level_length:
            xval = [detail[0]["Name"] for detail in recommendation_level_details[int(i)]]
            yval = [float(detail[0]["Price"]) for detail in recommendation_level_details[int(i)]]
            levle_data = go.Bar(x = xval, y = yval)
            level_title = F"level {i} data"
            level_layout = go.Layout(title = level_title)
            level_fig = go.Figure(data = levle_data, layout = level_layout)

            level_fig.show()
            continue
        elif i.isnumeric() and int(i) == 0:
            xval = [level for level in range(1, level_length+1)]
            yval = []
            for l in range(1, level_length+1):
                product_count = 0
                avg_price = 0
                for detail in recommendation_level_details[l]:
                    avg_price += float(detail[0]["Price"])
                    product_count += 1
                yval.append(avg_price/product_count)
            levle_data = go.Bar(x = xval, y = yval)
            level_title = F"all level price data"
            level_layout = go.Layout(title = level_title)
            level_fig = go.Figure(data = levle_data, layout = level_layout)

            level_fig.show()
            continue

        elif i == "exit":
            break
        else:
            print("Please enter valid integer or exit")
            continue

def main():
    run()
    
if __name__ == "__main__":
    main()



