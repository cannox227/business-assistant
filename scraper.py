import json
import concurrent.futures
import tqdm
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

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

def perform_google_search(key, value, description_only=True):
    result = google_search(value, description_only=description_only)
    return key, result

if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    
    company_name = input("Enter the company name: ")

    # Now, company_name contains the input provided by the user
    print(f"You entered: {company_name}")

    # Create a dictionary to map keys to query strings
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

    dict_company = {}
    dict_company["company_name"] = company_name

    max_threads = 12
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = []

        for key, value in query_dict.items():
            future = executor.submit(perform_google_search, key, value, False)
            futures.append(future)

        concurrent.futures.wait(futures)
        
        for future in futures:
            key, result = future.result()
            dict_company[key] = result

    with open(company_name.replace(' ', '_') + "_extraction.json", "w") as json_file:
        json.dump(dict_company, json_file, indent=4)
    
    print(f"Extraction completed. Results saved in {company_name.replace(' ', '_')}_extraction.json")