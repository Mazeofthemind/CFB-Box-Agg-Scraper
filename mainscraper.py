import untangle
import os
import re
from bs4 import BeautifulSoup

def scrapePlayerUrlLists(player_url_text):

    #Player ranking page contains invalid utf characters and is not valid xml, possibly intentional, ignore
    player_table = BeautifulSoup(player_url_text, "html.parser").tbody
    player_rows = player_table.find_all('tr')
    player_urls = map(lambda row: row.a['href'], player_rows)
    return player_urls

if __name__ == '__main__':
    rusher_text = open(os.path.join(".", "Rushing2018.html"), 'rb').read().decode('utf-8', 'ignore')
    receiver_text = open(os.path.join(".", "Receiving2018.html"), 'rb').read().decode('utf-8', 'ignore')
    rusher_urls = scrapePlayerUrlLists(rusher_text)
    receiver_urls = scrapePlayerUrlLists(receiver_text)