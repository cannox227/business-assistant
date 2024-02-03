from cat.mad_hatter.decorators import (
    tool,
    hook,
    plugin,
)
from pydantic import (
    BaseModel,
)
from datetime import (
    datetime,
    date,
)
import nltk
import json
from googlesearch import search
import concurrent.futures
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class MySettings(BaseModel):
    show_links : bool = False

    # required_int: int
    # optional_int: int = 69
    # required_str: str
    # optional_str: str = "meow"
    # required_date: date
    # optional_date: date = 1679616000

@hook  # default priority = 1 
def before_cat_reads_message(user_message_json, cat):
    fast_reply = "Ok, I will get that information for you."
    return

@plugin
def settings_model():
    return MySettings


@hook
def agent_prompt_prefix(prefix, cat):
    prefix = "You are a business assistant tasked with supporting the Sales Director in engaging potential clients for the company's offerings. \
            Your role involves meticulously gathering data from various platforms, analyzing the professional profiles and needs of each lead, particularly focusing on their job roles and industry experiences.\
            Utilize this information to craft customized, compelling messages and tailored value propositions that resonate with the unique requirements and challenges faced by each prospective customer. \
            Make the messages concise and straight to the point."
    return prefix

@hook 
def after_cat_bootstrap(cat):
    cat.settings = MySettings()
    nltk.download('punkt')
    nltk.download('stopwords')

def build_query_dict(company_name):
    query_dict = {
        'mission': "Which is the mission of " + company_name + "?",
        'vision': "Which is the vision of " + company_name + "?",
        'values': "Which are the values of " + company_name + "?",
        'founded': "When was " + company_name + " founded?",
        'founders': "Who founded " + company_name + "?",
        'headquarters': "Where is " + company_name + " headquartered?",
        'website': "What is the website of " + company_name + "?",
        'employees': "How many employees does " + company_name + " have?",
        'revenue': "How much revenue does " + company_name + " have?",
        'acquisitions': "How many acquisitions has " + company_name + " made?",
        'mergers': "How many mergers has " + company_name + " made?",
        'partnerships': "How many partnerships has " + company_name + " made?",
        'investments': "How many investments has " + company_name + " made?",
        'funding': "How much money has " + company_name + " raised?",
        'products': "Which are the products of " + company_name + "?",
        'services': "Which are the services of " + company_name + "?",
        'technologies': "Which are the technologies of " + company_name + "?",
        'patents': "How many patents does " + company_name + " have?",
        'research': "How much money does " + company_name + " spend on research?",
        'development': "How much money does " + company_name + " spend on development?",
        'innovation': "How much money does " + company_name + " spend on innovation?",
        'R&D': "How much money does " + company_name + " spend on R&D?",
        'industry': "In which industry is " + company_name + " in?",
        'competitors': "Who are the competitors of " + company_name + "?"
    }
    return query_dict

def perform_google_search(key, value, description_only=True):
    result = google_search(value, description_only=description_only)
    return key, result

def google_search(query, description_only=True):

    google_search_txt = search(query, advanced=True, sleep_interval=5, num_results=1)

    answers = {}
    for result in google_search_txt:
        if not description_only:
            answers['url'] = result.url
        try:
            answers['description'] = result.description
        except AttributeError:
            description = ""

    words = word_tokenize(answers['description'])
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalpha() and word.lower() not in stop_words]
    filtered_sentence = ' '.join(filtered_words)
    answers['description'] = filtered_sentence
            
    return answers

@tool
def get_company_information(company_name, cat):
    """Get information about a company. company_name is the name of the company you have to looking for.
    Return a dictionary with all the information about the company per each key of json file.
    Always return general information about the company like mission, vision, values, founded, founders, 
    headquarters, website, employees, revenue, acquisitions, mergers, partnerships, investments, funding, products, services,
    technologies, patents, research, development, innovation, R&D, industry, competitors.
    Always return the url associated to the information you have gathered from the dictionary."""

    query_dict = build_query_dict(company_name)
    dict_company = {}
    dict_company["company_name"] = company_name

    max_threads = 24
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = []

        for key, value in query_dict.items():
            future = executor.submit(perform_google_search, key, value, False)
            futures.append(future)

        concurrent.futures.wait(futures)
        
        for future in futures:
            key, result = future.result()
            dict_company[key] = result
    
    cat.send_ws_message("Extraction completed.")
    return dict_company

@tool
def get_company_information_short(company_name, cat):
    """Use previous gathered information and return a short version of each key of the dictionary in the following format.
    This is an example in case the company is Nokia:
    result = {
    Company Name: Nokia
    Mission: Creating a new world to transform our big planet into a small village. More info
    Vision: A future where digital, physical, and human domains merge to create immersive experiences. More info
    Values: Nokia's essentials include being open, fearless, and empowered. More info
    Founded: May, as a single paper mill operation. More info
    Founders: Not specified in the provided data. More info
    Headquarters: Espoo, Finland. More info
    Website: Nokia Phones
    Employees: Number of employees in decline. More info
    Revenue: Expectations for full year net sales and operating margin provided. More info
    Acquisitions, Mergers, Partnerships, Investments, Funding: Information about Nokia's acquisitions, mergers, partnerships, investments, and funding strategies. Acquisitions, Mergers, Partnerships, Investments, Funding
    Products & Services: Lists of products and services offered by Nokia. Products, Services
    Technologies & Patents: Overview of Nokia's technologies and patents. Technologies, Patents
    Research, Development, Innovation, R&D: Details on Nokia's research and development activities. Research, Development, Innovation, R&D
    Industry: Nokia operates in network infrastructure and advanced technologies. More info
    Competitors: Major competitors include Apple, LG, Oppo, Vivo, Microsoft, Samsung, Panasonic, Toshiba. More info
   }
   """    


    #  with open(company_name.replace(' ', '_') + "_extraction.json", "w") as json_file:
    #     json.dump(dict_company, json_file, indent=4)
    
    # print(f"Extraction completed. Results saved in {company_name.replace(' ', '_')}_extraction.json")



# @hook
# def before_cat_sends_message(message, cat):
#     prompt = f'Rephrase the following sentence in a grumpy way: {message["content"]}'
#     message["content"] = cat.llm(prompt)

#     return message
