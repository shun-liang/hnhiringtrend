import json
from .job_post import JobPost
class TestJobPost(object):
    '''Unit test for JobPost class
    '''

    example_text_single_word = '''
        Redwood City
        Numenta (http://www.numenta.com) is developing technology modeled on the neocortex. Get in on the ground floor of what, we think, is already groundbreaking
        machine intelligence.
        Senior devs with a passion for stellar, simple, usable design wanted. Experience with Python would be great but if you bring a deep skillset in a web stack
        of your choice then our team is always open to new ideas!
        Numenta is prepared to take on the world, and has the technology and experienced leadership to do it.
        Apply here (resume-eng at numenta dot com) or contact me through info in my profile for questions.
        P.S. Paid intern opportunities for the fall are open as well!
        Other keywords for page searchers: AI, Machine learning, front-end
    '''

    example_text_alias = '''
        Palo Alto, CA; Washington, DC (full-time preferred, part-time possible if you're an expert)
        REMOTE ONLY for now, but it'd be great if you were local -- we're building out a long-term team and will be setting up an office in the coming months.
        I'm with a 5-person team working on a real-time web + mobile application. We just finished a prototype, raised some seed money, and are headed for
        greatness. Hopefully. This is a chance to work on some architecture from the outset of the product. I'd prefer those who have a possibility of coming on
        long-term as I build out the team, most likely around Palo Alto, but do have immediate needs that lead me to consider splitting up short-term chunks of
        development for freelancers. In any case, we're distributed for now so remote is the only possibility.
        backend: postgres, python, django, gevent + gunicorn
        frontend: coffeescript, jQuery, backbone.js, socket.io, modernizr, compass
        I'm looking for:
        1. Advanced web jacks-of-many-trades. You know a lot about several things from above and have at least tried your hand at a demo app using the rest.
        Backend/frontend/deployment.
        2. A specialized front-end dev who knows their javascript in-and-out. We're designing a single page architecture for the most part. Mobile browser
        experience would be good.
        3. Mobile app developers (native iPhone & Android, though we're considering phonegap as well to get something out there faster).
        We're staying distributed for now -- I'm based in Palo Alto but spend a fair amount of time with some of the team in DC as well.
        gmail - davidmarble
        '''

    def test_match_programming_language(self):
        with open('./skills.json') as SKILLS_FILE:
            SKILLS_JSON = json.load(SKILLS_FILE)
            SINGLE_WORD_LANGUAGES = SKILLS_JSON['single_word_languages']
            MULTIPLE_WORD_LANGUAGES = SKILLS_JSON['multiple_word_languages']
            ALIASES = SKILLS_JSON['aliases']

        job_post = JobPost(self.example_text_single_word)
        job_post.match_single_word_languages(SINGLE_WORD_LANGUAGES)
        assert 'Python' in job_post.matched_languages 
        assert 'C++' not in job_post.matched_languages 
