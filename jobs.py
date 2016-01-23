from bs4 import BeautifulSoup
import json
import re
import requests

from threading import Thread

with open('skills.json') as skills_file:
    skills_json = json.load(skills_file)
    single_word_programming_languages = skills_json['single_word_languages']
    single_word_programming_languages_lower = [lang.lower() for lang in
            single_word_programming_languages]
    multiple_word_programming_languages = skills_json['multiple_word_languages']
    multiple_word_programming_languages_lower = [lang.lower() for lang in
            multiple_word_programming_languages]
    programming_languages_dict = {lang: [] for lang in
            single_word_programming_languages_lower +
            multiple_word_programming_languages_lower}
print(programming_languages_dict)

split_pattern = r'[\w\'\|\-\+#&]+'
url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = '[\w.-]+@[\w.-]+'

root_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/10822019.json')
job_post_ids = root_post_request.json()['kids']

def scrape_jobs():
    threads = []
    for job_post_id in job_post_ids:
        thread = Thread(target=_fetch_and_analyze, args=[job_post_id])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    print(programming_languages_dict)
    print({lang: len(programming_languages_dict[lang]) for lang in programming_languages_dict})

def show_jobs(job_post_id_list):
    print(job_post_json['text'])

def _get_job_post_text(job_post_id):
    job_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
            job_post_id)
    if job_post_request.status_code == 200:
        job_post_json = job_post_request.json()
        if 'text' in job_post_json:
            return job_post_json['text']
        else:
            print(job_post_request.text)
            return None
    else:
        print('Can\t retrive job post %s, HTTP response code: %s' % (job_post_id, job_post_request_status_code))
        return None

def _fetch_and_analyze(job_post_id):
    job_post_text = _get_job_post_text(job_post_id)
    if job_post_text:
        job_post_text = BeautifulSoup(job_post_text, 'html.parser').get_text(separator = ' ').lower()
        job_post_text = re.sub('%s|%s' % (url_pattern, email_pattern), '', job_post_text)
        words = re.findall(split_pattern, job_post_text)
        single_word_programming_languages_set = set({})
        multiple_word_programming_languages_set = set({})
        for word in words:
            if word in single_word_programming_languages_lower:
                single_word_programming_languages_set.add(word)
        for lang in multiple_word_programming_languages_lower:
            if lang in job_post_text:
                multiple_word_programming_languages_set.add(lang)
        for lang in single_word_programming_languages_set |\
            multiple_word_programming_languages_set:
            programming_languages_dict[lang].append(job_post_id)

if __name__ == '__main__':
    scrape_jobs()
