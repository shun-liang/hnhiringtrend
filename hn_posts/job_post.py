import re

class JobPost(object):
    ''' A job post scraped from Hacker News
    '''

    SPLIT_PATTERN = r'[\w\'\|\-\+#&’]+'

    def __init__(self, text):
        self.text = text
        self.words = []
        if text:
            self.words = re.findall(self.SPLIT_PATTERN, text)
        self.matched_languages = set({})

    def match_single_word_languages(self, langs):
        for word in self.words:
            if word in langs:
                self.matched_languages.add(word)
