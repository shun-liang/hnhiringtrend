from bs4 import BeautifulSoup
import html
import json
import re
import requests

with open('skills.json') as skills_file:
    programming_languages = json.load(skills_file)['languages']
    programming_languages_dict = {lang.lower(): [] for lang in
            programming_languages}
print(programming_languages_dict)

split_pattern = r'[\w\'\|\-+]+'
#tag_pattern = '<[^>*]>'
url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = '[\w.-]+@[\w.-]+'

root_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/10822019.json')
job_post_ids = root_post_request.json()['kids']

for job_post_id in job_post_ids:
    job_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
            job_post_id)
    if job_post_request.status_code == 200:
        job_post_json = job_post_request.json()
        if 'text' in job_post_json:
            job_post_text = BeautifulSoup(job_post_json['text'], 'html.parser').get_text(separator = ' ').lower()
            job_post_text = re.sub('%s|%s' % (url_pattern, email_pattern), '', job_post_text)
            words = re.findall(split_pattern, job_post_text)
            print(job_post_text)
            print(words)
            for word in words:
                if word in programming_languages_dict:
                    programming_languages_dict[word].append(job_post_id)
        else:
            print(job_post_request.text)
    else:
        print('Can\t retrieve job post %s' % job_post_id)

print(programming_languages_dict)
print({lang: len(programming_languages_dict[lang]) for lang in programming_languages_dict})
