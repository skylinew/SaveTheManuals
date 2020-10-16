import requests as request
from bs4 import BeautifulSoup
import random
from time import sleep
import time
from datetime import date
from requests_html import HTMLSession
import pymongo


def import_key(line_num, file_name):
    key = ''
    with open(file_name) as f:
        lines = f.readlines()
        key = lines[line_num-1]
    return key


# List of tuples for current cars with manual transmission
global_list = []
sample_list = [('Audi ', 'A3 Sedan'), ('Bmw ', 'M4'), ('Subaru ', 'WRX STI'), ('Subaru ', 'Exiga')]

# keys
_MONGO_URI = import_key(1, keys.txt)
_URLHOME = import_key(2, keys.txt)
_FILTER_URL = import_key(3, keys.txt)


_PRS = '- Present</a>'
_MAS = 'models and specs'
_SAP = 'specs and photos'
_MAT = 'Manual'
_mAT = 'manual'










'''
- Takes in an <a> tag containing href to make's web page
- Returns the make that this tag's href refers to 
'''
def extract_make(word):
    return word.split('/')[3].lower()

'''
- Takes in an <a> tag containing href to make's web page
- Returns the make that this tag's href refers to 
*** This is differs from 'extract_make()' since the <a> tag at the current-model's web page is different

'''
def extract_final_make(word):
    start = word.split('"')[3]
    return start[:start.find(' ')+1]


'''
- Takes in an <a> tag containing href to make's web page
- Returns the make that this tag's href refers to 
'''
def extract_model(word):
    title =  word.split('"')[3]
    after_title = title.split(' ', 1)[1]
    end = after_title.find('(') - 1
    return after_title[:end]


'''
- Takes in an <a> tag and checks if it contains a valid make
- Returns true or false
'''
def contains_valid_make(word, make_list):
    make = extract_make(word)
    if make in make_list:
        return True

    return False


'''
- Checks if current word is a valid reference to a make's web page
'''
def is_make_ref(word, make_list):
    if _MAS in word and contains_valid_make(word, make_list):
        return True
    return False

'''
- Checks if current word is a valid reference to a model's web page
'''
def is_model_ref(word):
    if _SAP in word:
        return True
    return False

'''
- Checks if current word is a valid reference to a current model's web page
'''
def is_present_ref(word):
    if _PRS in word:
        return True
    return False

'''
- Returns a list of car makes based on 'list_car_make.txt'
'''
def get_list_make(path):
    try:
        with open(path, 'r') as fp:
            text = fp.read().split('\n')
            return text
    except FileNotFoundError:
        print(path + ' not found')

'''
- Takes in a string in the format '<a href="https://URL/**INSERT MAKE**/" title="**INSERT MAKE** models and specs">'
- Parses the url, requests it, then returns the requested web page object
'''
def request_url(word):
    url = word.split('"')[1]
    return request.get(url)


'''
- To be used in has_manual_trans(), since autoevolution website has <dd> tag with manual html that is not displayed
- Iteratively finds the parent/ancestor of a tag until terminating case (<div ... style="display: none;"> is reached
- If terminating case is reached, then return True
- Alternatively, if parent reached is <body> (or <html>??) then return False
'''
def parent_display_none(ddtag):

    while True:
        if ddtag.get('style') == 'display: none;':
            return True
        if ddtag.parent is None or ddtag.name == 'body':
            return False
        if ddtag.parent is None:
            return False

        ddtag = ddtag.parent





'''
- Takes in request object that makes the current/present model car's web page
- Searches this web page to see if the car's current model comes in manual transmission
'''
def has_manual_trans(html):

    soup = BeautifulSoup(html, 'html.parser')

    for ddtag in soup.find_all('dd'):
        dd = ddtag.get_text()

        if (_MAT in dd or _mAT in dd) and (ddtag is not None) and (parent_display_none(ddtag) is False):
            print('---------------------------------------------')
            print(dd)
            print('---------------------------------------------')
            return True
    return False


'''
- Finds and gets the current model's web page
'''
def get_present_url(model_content):
    soup = BeautifulSoup(model_content, 'html.parser')
    for link in soup.find_all('a'):
        word = str(link)
        if is_present_ref(word):
            sleep(random.uniform(1, 3))
            #r_present_model = request_url(word)

            # dont forget to delete chunk below
            url = word.split('"')[1]
            session = HTMLSession()
            r_present_model = session.get(url)
            r_present_model.html.render(sleep=3, timeout=60.0)


            make = extract_final_make(word).lower().capitalize()
            model = extract_model(word)

            print('checking for manual...: ' + make + ' ' + model)

            # param for has_manual_trans in if statement was originally: r_present_model_text
            if has_manual_trans(r_present_model.html.html):
                print('Inserting ' + str((make, model)))
                global_list.append((make, model))

            session.close()
            return


'''
- Finds and gets all the models on the make's web page
'''
def get_model_urls(make_content):
    soup = BeautifulSoup(make_content, 'html.parser')
    for div in soup.find_all('div'):
        word = str(div)
        if len(word) < 650 and 'col2width bcol-white fl' in word and ' - present' in word:
            model_url =  word.split('"')[5]
            model_content = request.get(model_url)
            get_present_url(model_content.text)


'''
- Finds all manufacturers listed on the 'https://URL/cars/' homepage
- Requests the webpage for each manufacturer listed that is in the 'list_car_make.txt' file
'''
def get_make_urls(home_content):

    soup = BeautifulSoup(home_content, 'html.parser')
    make_list = get_list_make('list_car_make.txt')

    for link in soup.find_all('a'):
        word = str(link)
        if is_make_ref(word, make_list):
            sleep(random.uniform(1, 3))
            r_make = request_url(word)
            get_model_urls(r_make.text)



'''

        Filter global list so that only US manufactured/released cars are on the list

'''

def filter_global_list(filter_url, unfiltered_list):
    '''
    :param filter_url:      The website used to check if the car is US made or not
    :param unfiltered_list: The global list of cars compiled with manual transmission
    :return:                None, changes made to global list in place
    '''
    dictionary = {}


    for t in unfiltered_list:

        session = HTMLSession()

        search_query = (t[0] + t[1]).replace(' ', '+')
        print('search query: ' + filter_url + search_query)

        r_results = session.get(filter_url + search_query)

        # Sleep is crucial for render to work properly
        r_results.html.render(sleep=5)

        soup = BeautifulSoup(r_results.html.html, 'html.parser')

        if (soup is None) or (soup.find('div', 'total-links') is None):
            print('total-links is None')
            dictionary[t] = False
        else:
            for tag in soup.find('div', 'total-links'):
                print(tag)
                if int(tag.split()[1]) == 0:
                    dictionary[t] = False

        session.close()

    # Make corrections in global/unfiltered list by dictionary boolean values
    for key in dictionary.keys():
        for t in range(len(unfiltered_list)):
            if key == unfiltered_list[t]:
                unfiltered_list.pop(t)
                break

    return unfiltered_list

def insert_mongo(filtered_list):
    myclient = pymongo.MongoClient(_MONGO_URI)
    mydb = myclient["SaveTheManuals"]
    mycol = mydb["cars"]
    #y = mycol.delete_many({})
    current_time = date.today()
    doc = {"date": date.today(), "cars":[]}
    for car in filtered_list:
        make = car[0]
        if make == 'Bmw ':
            make = 'BMW'
        mydict = {"make": make, "model": car[1].rstrip()}
        doc["cars"].append(mydict)

    x = mycol.insert_one(mydict)
    print(x)

'''

    Returns the date of the previous month in yyyy-mm-dd format
'''
def get_prev_date(today):
    today = str(today)
    year = today.split('-')[0]
    month = today.split('-')[1]
    if month == '01':
        month = '12'
        year = str(int(year) - 1)
    else:
        month = str(int(month.lstrip('0')) - 1).zfill(2)

    return year + '-' + month + '-01'

'''
        To check if this newly compiled list is any different than the previous list
            If a change is detected: 
                Save the new list as a text file as "<date> \n list" with remove all mongodb entries, add all entries from new list to mongodb
            Else:
                Save a text file that has: "<date> \n no new changes" and name that file with <date>"no_change".txt
                
        Returns True if the last list is different than current
        Returns False otherwise
'''
def check_changes(filtered_list, today):
    recurse_flag = False
    prev_date = get_prev_date(today)
    prev_path = './filtered_lists/' + prev_date + '.txt'

    try:
        with open(prev_path, 'r') as f:
            # If prev text file has 'no changes' in the file content, recurse on the next file/month back
            lines = f.readlines()
            if lines[0] == 'no changes':
                recurse_flag = True
                f.close()
            # If prev file has actual list content, then compare this filtered_list and the list on the file
            else:
                listonfile = []
                for line in lines:
                    listonfile.append((line.split('~')[0], line.split('~')[1].rstrip()))

                if set(listonfile) == set(filtered_list):
                    print('No changes detected')
                    return False
                else:
                    print('Changes detected')
                    return True

    except IOError:
        return True

    if recurse_flag == True:
        check_changes(filtered_list, prev_date)

'''
        If changes_flag is True, write file with new list
        If changes_flag is False, write file with "no changes"
        
        File name must always be 'yyyy-mm-dd.txt'
'''
def write_new(changes_flag, filtered_list):
    save_path = './filtered_lists/' + str(date.today()) + '.txt'

    with open(save_path, 'w') as f:
        if changes_flag is False:
            f.write('no changes')
        else:
            for car in filtered_list:
                f.write(car[0] + '~' + car[1] + '\n')
        f.close()


if __name__ == "__main__":
    start = time.time()

    urlHome = 'https://www.autoevolution.com/cars/'

    

    '''
    r_home = request.get(urlHome)
    get_make_urls(r_home.text)
    print(global_list)

    elapsed = int(time.time() - start)
    print('Time Elapsed: ' + str(elapsed) + 's')
    
    '''

    global_list = filter_global_list(_FILTER_URL, global_list)
    
    changes_flag = check_changes(global_list, date.today())

    if changes_flag:
        insert_mongo(global_list)
        
    write_new(changes_flag, global_list)


    