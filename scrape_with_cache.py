from bs4 import BeautifulSoup, NavigableString #extract the html from the request
from selenium import webdriver #deal with the dynamic javascript
# from selenium.webdriver.support.ui import WebDriverWait
from multiprocessing import Process
import csv
import json
import time

#########################################
############### Scraping ################
#########################################

#URLs of the specific products
URLS = []

#Load the path of the driver for use
def load_driver_path():
    path_file = open('DriverPath.txt', 'r')
    path = path_file.read().strip()
    path_file.close()
    return path

#Loads all the urls from the URLS.txt file and appends them to the array of urls
def load_urls_from_text_file():
    urls_file = open('URLS.txt', 'r')
    urls = urls_file.readlines()
    for url in urls:
        URLS.append(url.strip())
    urls_file.close()

#Establish the webdriver
def link_driver(path_to_driver):
    # Establish the driver
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # driver = webdriver.Chrome(chrome_options=options, executable_path=path_to_driver)
    driver = webdriver.Chrome(path_to_driver)
    return driver

#  1. Loads the html data
#  2. Turns it into soup
def load_data(webdriver):
    field_names = ["Meta tags", "Name", "Description", "Category", "Price", "Image"]
    output_data = open('OutputData.csv', 'a')
    writer = csv.DictWriter(output_data, fieldnames=field_names)
    writer.writeheader()

    cache_dict = open_cache()
    for url in URLS:
        # Check if URL exists in cache
        if url in cache_dict.keys():
            print("Using Cache")
            # response = cache_dict[url]
            for item_property_dict in cache_dict[url]:
                writer.writerow(item_property_dict)
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
    print("meta_tags")
    print(meta_tags)
    return meta_tags

# gets the product name
def get_product_name(soup):
    product_name = soup.find('meta', property="og:description").get('content')
    print("product_name")
    print(product_name)
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
    print("data")
    # print(data.replace("\n", ""))
    # print(data.strip())
    print(data.split("\n"))
    print("catagory")

    category = ""
    for x in data.split("\n"):
        if x.strip() != "" and "Go to" not in x.strip():
            # print(x.strip())
            if category == "":
                category += x.strip()
            else:
                category += "/" + x.strip()
    print(category)
    # return '\n'.join([x for x in data.split("\n") if x.strip()!=''])
    return category

# gets the product price
def get_price(soup):
    # tag = soup.find('span', class_ = "op-value")
    tag = soup.find('span', class_ = "value")
    print("price")
    print(tag.text)
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

#  1. Links the driver
#  2. Loads the html data
#  3. Turns it into soup
#  4. extracts correct elements and loads it to csv file
def run():
    load_urls_from_text_file()
    path = load_driver_path()
    driver = link_driver(path)

    load_data(driver)
    # quit_driver(driver)


#########################################
############### Caching #################
#########################################

# Cache functions. Called wherever needed.
CACHE_FILENAME = 'productCache.json'

def open_cache():
    ''' Open the cache file or create a new cache dictionary
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        a cache dictionary
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        # cache_file = open(CACHE_FILENAME, 'a')
        cache_content = cache_file.read()
        cache_dict = json.loads(cache_content)
        cache_file.close()
    except:
        cache_dict = {}
    
    return cache_dict

def save_cache(cache_dict):
    ''' Save cache dictionary to the cache file
    Parameters
    ----------
    cache_dict: dictionary
        the cache dictionary
    
    Returns
    -------
    None
    '''
    dump_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, 'w')
    fw.write(dump_json_cache)
    fw.close()

def request_with_cache(url):
    ''' If URL in cache, retrieve the corresponding values from cache. Otherwise, connect to API again and retrieve from API.
    
    Parameters
    ----------
    url: string
        a URL
    
    Returns
    -------
    a string containing values of the URL from cache or from API
    '''
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

# To be done using graph data structure to analyze the top 3 level of 
# recommendation for related product from Costco when a customer 
# searched for the product.

def main():
    #create multiple threads for selenium web scraping - ASYNC
    processes = []
    p = Process(target=run, args=())
    processes.append(p)
    p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()


