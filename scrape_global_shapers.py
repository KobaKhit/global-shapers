
# coding: utf-8

import pandas as pd
import urllib.request, json 

from bs4 import BeautifulSoup
from tqdm import tqdm
import pprint as pp

def scrape_hub(hub):
    # Scrapes the webpage of a global shapers hub for members.
    # Args:
    # - slug: string - slug for the url, ex.g. abu-dhabi-hub
    url = 'https://www.globalshapers.org/hubs/' + hub
    
    f = urllib.request.urlopen(url)
    f = f.read().decode('utf-8')
    r = BeautifulSoup(f,"html.parser")
    # Scrape using bs4
    containers = r.find_all(class_='hub__person') # list of members
    members = []
    classes = ['hub__person__text__name','hub__person__role']
    for c in containers:
        mem = dict() # one member
        for cl in classes: 
            val = c.find(class_=cl)
            mem.update({cl.split('__')[-1]: val.text.strip() if val is not None else 'None' })

        # edge case for description
        val = c.find_all(class_='hub__person__text__item')
        val = ' '.join([v.text.strip() for v in val])
        mem.update({'description': val})
        
        members.append(mem)
        
    return({'hub': hub,'members': members})


def main():
    with urllib.request.urlopen("https://www.globalshapers.org/hubs.json") as url:
        data = json.loads(url.read().decode())

    gs = pd.DataFrame(data['items'])

    f = urllib.request.urlopen("https://www.globalshapers.org/hubs/philadelphia-hub")
    f = f.read().decode('utf-8')
    r = BeautifulSoup(f,"html.parser")


    containers = r.find_all(class_='hub__person')
    members = []
    classes = ['hub__person__text__name','hub__person__role']
    for c in containers:
        mem = dict()
        for cl in classes: 
            val = c.find(class_=cl)
            mem.update({cl.split('__')[-1]: val.text.strip() if val is not None else 'None' })

        # edge case
        val = c.find_all(class_='hub__person__text__item')
        val = ' '.join([v.text.strip() for v in val])
        mem.update({'description': val})

        members.append(mem)

    globalshapers = []
    for s in tqdm(gs['slug']): # scrape all shaper hubs websites
        hub = scrape_hub(s)
        globalshapers.append(hub)

    # save as json
    with open('all_hubs.json', 'w') as fp: 
        json.dump(globalshapers, fp)

    # create member table
    member_table = pd.DataFrame()
    for h in globalshapers:
        hub = h['hub']
        df = pd.DataFrame(h['members'])
        df['hub'] = hub
        member_table = member_table.append(df)

    # Parse company from description
    # member_table['company'] = member_table['description'].str.split('@').iloc[:,1]
    # member_table.head()
    garbage, company = member_table['description'].str.split('@', 1).str
    member_table['company'] = company
    member_table.head()

    # join with gs table from the Global Shapers website
    GlobalShapers = pd.merge(gs,member_table,left_on='slug', right_on='hub')
    GlobalShapers.describe()

    # save to csv
    GlobalShapers.to_csv('Global_Shapers.csv', index = False)
    
if __name__ == '__main__':
    main()

