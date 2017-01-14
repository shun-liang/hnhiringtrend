import json
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
from bs4 import BeautifulSoup

THREAD_POOL_SIZE = 15

with open('skills.json') as SKILLS_FILE:
    SKILLS_JSON = json.load(SKILLS_FILE)
    SINGLE_WORD_LANGUAGES = SKILLS_JSON['single_word_languages']
    MULTIPLE_WORD_LANGUAGES = SKILLS_JSON['multiple_word_languages']
    ALIASES = SKILLS_JSON['aliases']

try:
    with open('language_matches.json', 'r+') as language_matches_file:
        UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT = json.load(language_matches_file)
except FileNotFoundError:
    UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT = {}

try:
    with open('checked_posts.json', 'r+') as checked_posts_file:
        checked_posts = set(json.load(checked_posts_file)['checked_posts'])
except FileNotFoundError:
    checked_posts = set({})

try:
    with open('total_posts.json', 'r+') as total_posts_file:
        total_posts = json.load(total_posts_file)['total_posts']
        total_posts_json = {'total_posts': total_posts}
except FileNotFoundError:
    total_posts = {}
    total_posts_json = {'total_posts': total_posts}

with open('posts.json') as posts_file:
    POSTS_JSON = json.load(posts_file)
    JOB_POST_POINTERS = POSTS_JSON['pointers']
    NON_JOB_POSTS = POSTS_JSON['non_job_post']

SPLIT_PATTERN = r'[\w\'\|\-\+#&’]+'
URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
EMAIL_PATTERN = r'[\w.-]+@[\w.-]+'

def scrape_jobs(root_post_id):
    if str(root_post_id) in JOB_POST_POINTERS:
        root_post_id = JOB_POST_POINTERS[str(root_post_id)]
    if root_post_id  in NON_JOB_POSTS:
        print('%s is not a job post' % root_post_id)
        return None
    if root_post_id in checked_posts:
        print('post %s already scraped' % root_post_id)
        return None
    root_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
                                     str(root_post_id))
    root_post_json = root_post_request.json()
    if 'time' not in root_post_json:
        print('time attribute not in post %s' % root_post_id)
        return None
    unix_time = root_post_json['time']
    unix_time_str = str(unix_time)
    post_datetime = datetime.fromtimestamp(unix_time)
    if 'title' in root_post_json:
        root_post_title = root_post_json['title']
        if "hiring" in root_post_title.lower():
            print('%s: %s' % (root_post_title, root_post_request.url))
            job_post_ids = root_post_json['kids']
            total_posts[unix_time_str] = len(job_post_ids)
            futures = []
            executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
            if unix_time_str in UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT:
                programming_languages_dict = UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT[unix_time_str]
            else:
                programming_languages_dict = {lang: [] for lang in
                                              SINGLE_WORD_LANGUAGES + MULTIPLE_WORD_LANGUAGES}
                UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT[unix_time_str] = programming_languages_dict
            existing_posts = frozenset([post for posts in programming_languages_dict.values() for post in posts])
            for job_post_id in job_post_ids:
                if job_post_id not in existing_posts:
                    task_future = executor.submit(_fetch_and_analyze, job_post_id, programming_languages_dict)
                    futures.append(task_future)
                #else:
                #    print('job post %s already scraped.' % job_post_id)
            for task_future in futures:
                task_future.result()
    else:
        print('Can\'t get attribute \'title\' from root post %s' % root_post_request.url)
    now = datetime.now()
    if post_datetime.month != now.month or post_datetime.year != now.year:
        checked_posts.add(root_post_id)

def show_jobs(job_post_id_list):
    for job_post_id in job_post_id_list:
        print(_get_job_post_text(job_post_id))

def main():
    for root_post in get_all_whoishring_root_posts():
        scrape_jobs(root_post)
    with open('language_matches.json', 'w') as language_matches_file:
        json.dump(UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT, language_matches_file, indent=2)
    with open('language_matches.jsonp', 'w') as language_matches_jsonp_file:
        language_matches_jsonp_file.write('var languages_matches = %s' % json.dumps(UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT))
    with open('checked_posts.json', 'w') as checked_posts_json_file:
        checked_posts_json = {'checked_posts': list(checked_posts)}
        json.dump(checked_posts_json, checked_posts_json_file, indent=2)
    with open('total_posts.json', 'w') as total_posts_json_file:
        json.dump(total_posts_json, total_posts_json_file, indent=2)
    with open('total_posts.jsonp', 'w') as total_posts_jsonp_file:
        total_posts_jsonp_file.write('var total_posts = %s' % json.dumps(total_posts_json))

def get_all_whoishring_root_posts():
    user_request = requests.get('https://hacker-news.firebaseio.com/v0/user/whoishiring.json')
    if user_request.status_code == 200:
        root_posts = user_request.json()['submitted']
    user_request = requests.get('https://hacker-news.firebaseio.com/v0/user/_whoishiring.json')
    if user_request.status_code == 200:
        root_posts += user_request.json()['submitted']
    print('root_posts: %s' % root_posts)
    return root_posts

def reduce_all_language_matches():
    reduced_dict = {lang: [] for lang in SINGLE_WORD_LANGUAGES + MULTIPLE_WORD_LANGUAGES}
    for unix_time in UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT:
        language_dict = UNIX_TIME_TO_PROGRAMMING_LANGUAGES_DICT[unix_time]
        for lang in language_dict:
            reduced_dict[lang] += language_dict[lang]
    return reduced_dict

def _get_job_post_text(job_post_id):
    job_post_request = requests.get('https://hacker-news.firebaseio.com/v0/item/%s.json' %
                                    job_post_id)
    if job_post_request.status_code == 200:
        job_post_json = job_post_request.json()
        if job_post_json:
            if 'text' in job_post_json:
                return job_post_json['text']
            else:
                return None
        else:
            print('Can\'t get json of job post %s, job_post_json is null' % job_post_id)
            return None
    else:
        print('Can\'t retrive job post %s, HTTP response code: %s' %
              (job_post_id, job_post_request.status_code))
        return None

def _fetch_and_analyze(job_post_id, programming_languages_dict):
    job_post_text = _get_job_post_text(job_post_id)
    if job_post_text:
        job_post_text = BeautifulSoup(job_post_text, 'html.parser').get_text(separator=' ')
        job_post_text = re.sub('%s|%s' % (URL_PATTERN, EMAIL_PATTERN), '', job_post_text)
        words = re.findall(SPLIT_PATTERN, job_post_text)
        single_word_languages_set = set({})
        multiple_word_languages_set = set({})
        for word in words:
            if word in SINGLE_WORD_LANGUAGES:
                single_word_languages_set.add(word)
            if word in ALIASES:
                single_word_languages_set.add(ALIASES[word])
        for lang in MULTIPLE_WORD_LANGUAGES:
            if lang in job_post_text:
                multiple_word_languages_set.add(lang)
        for lang in single_word_languages_set |\
            multiple_word_languages_set:
            programming_languages_dict[lang].append(job_post_id)

if __name__ == '__main__':
    main()
