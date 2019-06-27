#coding=utf8

'''
Anna Bonazzi, 26/06/2019
# Script to scrape the transcripts of Boder's Shoah survivor interviews from http://voices.iit.edu/ using XPath

'''
# To time the script
from datetime import datetime
startTime = datetime.now()

import os, glob, re
from lxml import html
import requests

#--------------------------

##################################
# Main function
def scraper(link, further):
    # Retrieves page
    page = requests.get(link)
    # Saves parsed results
    tree = html.fromstring(page.content)
    tt = (str(page.content))
    # Picks chosen content
    further_lks = tree.xpath(further)
    
    return (further_lks, tree)
##################################
    
# Gets links to each person's page
base = 'http://voices.iit.edu'
main_link = base+'/search_results?filter_by=name'

further_1 = '//ul[@class="result_list"]/li/a/@href'
name_lks, tree = scraper(main_link, further_1)
for i in range(0, len(name_lks)):
    name_lks[i] = base+name_lks[i].strip('.')
    
# Gets links from person page to transcripts page
trans_lks = []
trad_lks = []
names = {}
further_2 = '//li[@id="transcript"]/p/a/@href' # Link to text
further_3 = '//div[@id="content"]/h1/text()' # Person's name
further_4 = '//li[@id="transcript"]/p/a/text()' # Name of link (transcr. or transl.)

for name_lk in name_lks:
    # Gets link to texts
    trans_lk, tree = scraper(name_lk, further_2)
    # Gets person's name
    name = tree.xpath(further_3)[0].strip()
    # Gets separate links for transcription and translation
    texts = tree.xpath(further_4)
    if len(texts) == 2:
        trans_lks.append(trans_lk[0])
        trad_lks.append(trans_lk[1])
        names[name] = [trans_lk[0], trans_lk[1]]
       
    else: # Some have no translation (transcript is already in English) or no original transcription
        if 'English' in texts[0]:
            trad_lks.append(trans_lk[0])
            names[name] = ['no_transcript', trans_lk[0]]
        else:
            trans_lks.append(trans_lk[0])
            names[name] = [trans_lk[0], 'no_translation']

# Gets text of transcription / translation
for n in names:
    
    # Transcript (for translation, change numbers from 0 to 1, and adjust output path below)
    if not 'no_t' in names[n][0]:
        # Gets speaking times line by line
        trans_times, tree = scraper(base+'/'+names[n][0], '//div[@id="content"]/ul/li/span[@class="utterance"]/@start')

        # ? Text units get multiplied because each i or a creates a new entry. How to make them one? (fixed it at the output printing phase)
        
        # Gets text lines
        trans_txt, tree = scraper(base+'/'+names[n][0], '//div[@id="content"]/ul/li/span//text()')
        
        # Shows person being processed, lines length
        print(n, str(len(trans_times)), str(len(trans_txt)), str(len(('\n'.join(trans_txt)).split('\n\n')))) #, '\n'.join(trans_txt)
        
       
        # Renames transcripts by person and ID
        if n == 'Dr. Leon Frim':
            n = 'Leon Frim'
        
        # Pause ID's - they are all messed up
        '''
        ids = {}
        with open('/Users/anna/Google_Drive/GSRM_2019_Boder/boder_ids.txt', 'r') as fl:
            for line in fl:
                ids[line.split('\t')[1].strip('\n')] = line.split('\t')[0]
        filename = ids[n]+'_'+n.replace(' ', '_')
        '''
        
        filename = n.replace(' ', '_')
        
        # Prints out individual transcripts
        count = 0
        with open('/Users/anna/Google_Drive/GSRM_2019_Boder/Boder_transcripts_original/Boder_transcr_'+filename+'.txt', 'w') as out:
            # Adjust output format
            final = ('\n'.join(trans_txt)).split('\n\n')
            for f in final:
                line = f.replace('\n', '').strip(' ').replace('            ', '\t')
                # Add speaking times to lines
                if ':\t' in line:
                    try:
                        line = trans_times[count]+'\t'+line
                        count += 1
                    except:
                        print(trans_times)   
                out.write(line+'\n')
        
        
#--------------------------
# To time the script
time = datetime.now() - startTime
print ("\n(Script running time: " + str(time) + ")")
