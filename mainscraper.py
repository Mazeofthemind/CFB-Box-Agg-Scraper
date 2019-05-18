import re
from bs4 import BeautifulSoup, Comment
import requests
import json
import time
import logging

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

def scrapePlayerUrlLists(player_url_text):
    '''
    
    '''
    #Player ranking page contains invalid utf characters and is not valid xml, possibly intentional, ignore
    player_table = BeautifulSoup(player_url_text, "html.parser").tbody
    player_rows = player_table.find_all('tr')
    player_urls = map(lambda row: row.a['href'], player_rows)
    return player_urls

def passing_processor(soup_obj):
    '''
    
    '''
    comments = soup_obj.findAll(text=lambda text:isinstance(text, Comment))
    passing_table = BeautifulSoup(comments[0].extract(), 'html.parser').find('table')
    return None
def running_recieving_processor(soup_obj, game_id):
    '''
    
    '''
    comments = soup_obj.findAll(text=lambda text:isinstance(text, Comment))
    running_receiving_table = BeautifulSoup(comments[0].extract(), 'html.parser').find('table')
    running_receiving_rows = running_receiving_table.find('tbody').findAll('tr')
    def player_row_processor(row, game_id):
        #Tests for the presence of a class attribute to filter out the internal table header
        if(row.has_attr('class')):
            return None
        name = row.find('th').text
        logging.debug("Processing player {}".format(name))
        
        #Note that we are only extracting basic stats, things like x per attempt can be
        #re-calculated as necessary
        columns = row.findAll('td')
        team_name = columns[0].text
        rush_att = columns[1].text
        rush_yrds = columns[2].text
        rush_td = columns[4].text
        rec = columns[5].text
        rec_yrds = columns[6].text
        rec_td = columns[8].text
        return (game_id, name, team_name, rush_att, rush_yrds, rush_td, rec, rec_yrds, rec_td)

    box_stat_tuples = list(map(lambda x: player_row_processor(x, game_id), running_receiving_rows))
    #Remove the None values inserted where the internal headers were removed
    filtered_box_stat_tuples = list(filter(lambda x: x != None, box_stat_tuples))
    return filtered_box_stat_tuples

def soup_parse_box_score(html_text, game_id):
    '''
        Accept beautiful soup object for the game box score html, return two lists of passing
        and receiving/running player stats
    '''
    soup = BeautifulSoup(html_text, 'html.parser')
    
    passing_div = soup.find('div', {'id': 'all_passing'})
    passing_processor(passing_div)
    
    #Works around a really annoying trick of hiding the table in a comment
    running_receiving_div = soup.find('div', {'id': 'all_rushing_and_receiving'})
    running_receiving_stats = running_recieving_processor(running_receiving_div, game_id)
    
    #Add the game_id to reach row to assist in post-aggregation identification
    print(running_receiving_stats)
    return running_receiving_stats

def extract_box_score(start_url, config):
    '''
    
    '''
    game_id = start_url.split('/')[3].split('.')[0]
    print(game_id)
    complete_url = config['base_url'] + start_url 
    box_score_request = requests.get(complete_url, headers=headers)
    box_score_text = box_score_request.text
    with open('./game_box_score.html', 'w') as cache_handle:
        cache_handle.write(box_score_text)
        
    box_stats = soup_parse_box_score(box_score_text, game_id)
    return box_stats

def parse_game_week_page(html_text):
    '''
    Receive beautiful soup object representing the relevant football games for a particular week
    extract a list of urls to access the box scores of each game and a url to the next week
    of games
    '''
    soup = BeautifulSoup(html_text, 'html.parser')
    game_table_elements = soup.findAll("td", {"class": "gamelink"})
    print(game_table_elements)
    game_table_links = list(map(lambda element: element.find("a")['href'], game_table_elements))
    
    logging.info("{} games scraped for week".format(len(game_table_links)))
    
    #Get the link to the next week of games by filtering all the links in the page down to one
    #with known text content
    all_links = soup.findAll("a")
    next_week_link_element = list(filter(lambda element: element.text == "Next Week", all_links))
    print(next_week_link_element)
    next_week_link = next_week_link_element[0]["href"]
    
    return (game_table_links, next_week_link)

def extract_year_game_urls(start_url, config):
    '''
    
    '''
    week_max = 1
    #Generate full url
    current_url = config['base_url'] + start_url
    
    year_game_links = []
    
    week_crawler_continue_flag = True
    week_counter = 0
    while week_crawler_continue_flag:
        
        #Request the week of games
        logging.info("Grabbed week of game links from {}".format(current_url))
        game_week_request = requests.get(current_url, headers=headers)
        
        #Cache the html text in a flat file
        with open('./game_week_page.html', 'w') as cache_handle:
            cache_handle.write(game_week_request.text)

        game_table_links, next_week_link = parse_game_week_page(game_week_request.text)
        year_game_links += game_table_links
        week_counter += 1
        
        current_url = config['base_url'] + next_week_link
        
        if week_counter == week_max:
            week_crawler_continue_flag = False

        #
        logging.info("Resting for configured {}".format(config['sleep_time_s']))
        time.sleep(config['sleep_time_s'])
    
    logging.info("Completed annual game link retrieval, {} retrieved".format(len(year_game_links)))
    
    return year_game_links
    

if __name__ == '__main__':
    with open('./config.json', 'r') as config_handle:
        config = json.load(config_handle)
    #'boxscores/index.cgi?month=9&day=1&year=2018'
    years = ['2018']
    conferences = ['big-ten']
    
    #
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
    
    #Takes each of the specified years and establishes a starting point for the crawler
    boxscore_starting_urls = []
    for year in years:
        for conference in conferences:
            starting_url = "/cfb/boxscores/index.cgi?month=9&day=1&year={}&conf_id={}".format(year, conference)
            boxscore_starting_urls.append(starting_url)
            
    
    #Iterate through list of starting urls and 
    boxscore_starting_urls = boxscore_starting_urls[:1] #For testing use only the first starting url
    game_url_lists = list(map(lambda x: extract_year_game_urls(x, config), boxscore_starting_urls))
    flattened_game_urls = [item for sublist in game_url_lists for item in sublist]
    
    flattened_game_urls = flattened_game_urls[:1]
    box_scores = list(map(lambda x: extract_box_score(x, config), flattened_game_urls))
    print(box_scores)