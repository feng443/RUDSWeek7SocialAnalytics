# Core
from datetime import date, datetime, timezone, timedelta
import re

# Logging
import sys
import logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    stream=sys.stdout) # Needed in Jupyter. Comment out if only need to see in log file.

# Scheduler
import schedule

# Numpy, Pandas and PyPlot
import pandas as pd
from matplotlib import pyplot as plt, use
use('Agg') # Try to get around with issue with TK error in Heroku
import seaborn as sns

sns.set()
sns.set_style(
    'darkgrid',
    {
        'axes.facecolor': '0.9',
        'axes.titlesize': 'x-large',
        'figure.titlesize': 'x-large',
    }
)

# API
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Own
from twitter_config import *

SLEEP_SEC = 60 * 1
PAGE_SIZE = 2
PAGES = 1
TODAY = date.today().strftime('%m/%d/%y')

_AUTH = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
_AUTH.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)

TWITTER_API = tweepy.API(_AUTH, parser=tweepy.parsers.JSONParser())
SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()

TWEET_FROM = '@feng443'
TWEET_TO = 'chanfengcom'

DEBUG = True
LOG_FILE = 'PlotBot.log'

class PlotBot(object):
    _analyzed = []
    _to_analyze = []
    _df = pd.DataFrame(index=pd.Index(
        list(range(-PAGE_SIZE * PAGES)),
        name='Tweets Ago'))

    @property
    def data(self):
        return self._df

    @property
    def logger(self):
        logger = logging.getLogger('PlotBot')
        if self._debug:
            logger.setLevel(logging.DEBUG)
        if self._log_file:
            logger.addHandler(logging.FileHandler(self._log_file))
        return logger

    def __init__(self, debug=False, log_file=None,
                 ignore_old=True):
        self._re = re.compile('Analyze: @(\w{1,15})')
        self._debug = debug
        self._log_file = log_file
        self._ignore_old = ignore_old

    def _scan_tweets(self, debug=True):
        self.logger.info('Scan tweets ...')
        self._tweets = []
        for tweet in TWITTER_API.search(TWEET_FROM, count=PAGE_SIZE)['statuses']:
            targets = self._re.findall(tweet['text'])
            if targets:
                target = targets[0]
                requester = tweet['user']['screen_name']
            else:
                continue
            self.logger.debug(f'{requester} ask for {target}')
            if target not in self._analyzed:
                if self._ignore_old and self._is_old_tweet(tweet):
                    self.logger.debug('is_old_tweet: {}'.format(self._is_old_tweet(tweet)))
                    self.logger.info('Skip older tweets.')
                    break
                self.logger.debug(f'Put into _to_analyze({target}, {requester})')
                self._to_analyze.append((target, requester))
                # created_at = tweet['created_at']
            else:
                self.logger.info(f'{target} already analyzed. Skip.')

    def _is_old_tweet(self, tweet):
        tweet_datetime = datetime.strptime(
            tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")
        self.logger.debug(f'tweet time: {tweet_datetime}')
        now = datetime.now(timezone.utc)
        self.logger.debug(f'now: {now}')
        return (now - tweet_datetime) > timedelta(seconds=SLEEP_SEC * 2) # Times 2 to allow some processing time buffer

    def _analyze_all(self):
        if not self._to_analyze:
            self.logger.info('Nothing new.')
            return

        self.logger.info('Analyze all ...')
        while self._to_analyze:
            (target, requester) = self._to_analyze.pop()
            self._analyzed.append(target)
            self._analyze(target, requester)
            self._plot(target, requester)
            self._tweet_out(target, requester)

    def _analyze(self, target, requester):
        self.logger.info(f'Analyze {target}, requested by {requester}')
        tweets_ago = 0
        for page in range(PAGES):
            for tweet in TWITTER_API.user_timeline(target, count=PAGE_SIZE, page=page):
                self._df.at[tweets_ago,
                            f'@{target}'] = SENTIMENT_ANALYZER.polarity_scores(tweet['text'])['compound']
                tweets_ago -= 1

    def _plot(self, target, requester):
        fig, ax = plt.subplots(figsize=(8, 6))
        self.data.plot.line(
            y=f'@{target}',
            marker='o',
            ax=ax,
            alpha=0.8,
        )
        plt.legend(
            title='Tweets',
            bbox_to_anchor=(1.25, 1)
        )
        plt.title(f'Sentiments Analysis of Tweet ({TODAY}), requeted by {requester}',
                  fontsize=16)
        plt.ylabel('Tweet Polarity')
        plt.gca().invert_xaxis()

        plt.savefig('plot_bot.png', bbox_inches='tight')
        #plt.show()

    def _tweet_out(self, target, requester):
        self.logger.info(f'Tweet out  ...{target}')
        TWITTER_API.update_with_media('plot_bot.png',
                                      f'@{requester} Sentiment Analsyis of Tweets ({TODAY}), requested by {requester}')

    def listen(self):
        self._scan_tweets()
        self._analyze_all()

def main():
    print('Starting PlotBot...')
    schedule.clear()
    bot = PlotBot(debug=DEBUG, log_file=LOG_FILE, ignore_old=True)
    schedule.every(SLEEP_SEC).seconds.do(bot.listen)
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    main()
