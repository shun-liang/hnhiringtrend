from bs4 import BeautifulSoup
import json
import re
import requests

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

THREAD_POOL_SIZE = 15

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

#with open('posts.json') as posts_file:
#    posts_json = json.load(posts_file)

split_pattern = r'[\w\'\|\-\+#&]+'
url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = '[\w.-]+@[\w.-]+'

def scrape_jobs(root_post_id):
    root_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
            str(root_post_id))
    root_post_json = root_post_request.json()
    if 'title' in root_post_json:
        root_post_title = root_post_json['title']
        if "Ask HN: Who is hiring?" in root_post_title:
            print ('%s: %s' % (root_post_title, root_post_request.url))
            job_post_ids = root_post_json['kids']
            futures = []
            executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
            for job_post_id in job_post_ids:
                task_future = executor.submit(_fetch_and_analyze, job_post_id)
                futures.append(task_future)
            for task_future in futures:
                task_future.result() 
    else:
        print('Can\'t get attribute \'title\' from root post %s' % root_post_request.url)

def show_jobs(job_post_id_list):
    print(job_post_json['text'])

def _get_all_whoishring_root_posts():
    user_request = requests.get('https://hacker-news.firebaseio.com/v0/user/whoishiring.json')
    if user_request.status_code == 200:
        root_posts = user_request.json()['submitted']
        return root_posts

def _get_job_post_text(job_post_id):
    job_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
            job_post_id)
    if job_post_request.status_code == 200:
        job_post_json = job_post_request.json()
        if job_post_json:
            if 'text' in job_post_json:
                return job_post_json['text']
            else:
                #print(job_post_request.text)
                return None
        else:
            print('Can\'t get json of job post %s, job_post_json is null' % job_post_id)
            #raise Exception('Can\'t get json of job post %s' % job_post_id)
            return None
    else:
        print('Can\'t retrive job post %s, HTTP response code: %s' %
                (job_post_id, job_post_request.status_code))
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
    #for post_id in  posts_json.values():
    #    scrape_jobs(post_id)
    for root_post in _get_all_whoishring_root_posts():
        scrape_jobs(root_post)
    ordered_programming_languages_dict = OrderedDict(sorted(programming_languages_dict.items(), key=lambda t: len(t[1])))
    print(ordered_programming_languages_dict)
    print(OrderedDict(sorted({lang: len(ordered_programming_languages_dict[lang]) for lang in
        ordered_programming_languages_dict}.items(), key=lambda t: t[1])))
