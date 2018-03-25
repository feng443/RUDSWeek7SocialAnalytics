# Unit 7 / Assignment - Distinguishing Sentiments

## News Mood

* [NewsMood.ipynb](NewsMood.ipynb)
* [NewsMood.md](NewsMood.md)
* [NewsMood_scatter.png](NewsMood_scatter.png)
* [NewsMood_bar.png](NewMood_bar.png)

## Plot Bot

Meanwhile, I found that matplotlib has issue on Heroku and found a workaround on StackOverflow: https://github.com/matplotlib/matplotlib/issues/9017

``` python
import pandas as pd
import matplotlib
matplotlib.use('agg')   # Try to get around with issue with TK error in Heroku
```
* [plot_bot.py](plot_bot.py) - The main Python code file
* [requirements.txt](requirements.txt) - Required modules when deploying to Heroku
* [Procfile](Procfile) - Heroku Procfile
* [plot_bot.png](plot_bot.png) - Sample plot

I used following commands to deploy the code to Heroku:

```bash
heroku create plot-bot
heroku git add .
heroku git commit -am 'Ready to be deploy to Heroku'
git push heroku master
heroku ps:scale 1
heroku logs --tail
```
I used my main twitter account for charts: https://twitter.com/feng443

Then test from my other Twitter account: chanfengcom and sent command: "@feng443 Analyze: @CNN".


