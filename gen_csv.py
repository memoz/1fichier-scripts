#!/usr/bin/env python3

import csv, pytz, requests
from bs4 import BeautifulSoup
from datetime import datetime

# Check cookies
cookies = dict(LG='en', SID='be-sure-to-fill-this-in')
print('{} Checking cookies...'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
r = requests.get('https://1fichier.com/', cookies = cookies)
if r.text.find('your-email-address') == -1:
    raise SystemExit('Invalid cookies! Expired?')

# Get list
print('{} Requesting list...'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
payload = {'dir_id': '0', 'oby': '0'}
r = requests.get('https://1fichier.com/console/files.pl', params = payload, cookies = cookies)
list_filename = '1fichier_files_list_{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M%S'))

# Parse it
print('{} Parsing html...'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
soup = BeautifulSoup(r.text, 'lxml')
ul = soup.find("ul", class_ = 'jqueryFileTree')
li = ul.find_all("li", recursive = False)

# Set 1fichier timezone
remote_tz = pytz.timezone("Europe/Paris")

# Convert to CSV
print('{} Generating {}...'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), list_filename))
with open(list_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['ref_id', 'file_name', 'available_time'])
    items_written = 0
    for tag in li:
        children_list = list(tag.stripped_strings)
        naive_dt = datetime.strptime(children_list[1], '%d/%m/%Y %H:%M')
        remote_tz_dt = remote_tz.localize(naive_dt, is_dst = None)
#        utc_dt = remote_tz_dt.astimezone(pytz.utc)
        _ = writer.writerow([tag['rel'].replace('C_0_', '', 1), children_list[0], remote_tz_dt.strftime('%Y-%m-%d %H:%M:%S%z')])
        items_written += 1

# Done
print('{} {} item(s) written.'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), items_written))
