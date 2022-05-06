# Availability Bot

A Python bot that checks a list of sites for product availability and sends alerts via webhooks (e.g. Discord or Slack).

## Usage

- Clone this repository
- Set the WEBHOOK_ALERT and WEBHOOK_PULSE environment variables (using [Slack](https://api.slack.com/messaging/webhooks), or [Discord](https://discord.com/developers/docs/resources/webhook#execute-webhook))
- Download a browser driver compatible with the one you have installed [here](https://www.selenium.dev/downloads/#platforms-supported-by-selenium)
- Edit the bot.py script changing the web driver's path to the one you downloaded
- Install [Python 3](https://www.python.org/downloads/)
- Install the requirements: `pip install -r requirements.txt`
- Run the script: `./bot.sh`

## Context

NVidia's RTX 30 series cards were released mid-2020, during the COVID-19 pandemic.
For that reason, supply chains were slow and demand for home-office hardware rose up, resulting in very low stock available for those items.
In the mentioned stores, we had something like 5 units per week, made available at random hours during the days.
To release me from constantly pressing F5 in these stores' GPU sections, I made this bot.

## How it works

This bot uses [Selenium](https://www.selenium.dev/) to launch a Chrome instance, access the pages I configured and look for a "buy" button.
If the button is found, it plays a sound (in case I'm not using the computer; e.g. Kabum updates it's stock at 3 a.m. every day) and sends a message to my Slack
notifications channel, which then vibrates my smartwatch.

As many other websites, these stores try to identify and block bots.
As a workaround, I removed the automation flag from the Selenium driver's request headers and a new UserAgent header is generated at every loop iteration.
I also added a random sleep time between requests and used the same browser instance to access sequentially all the stores, so the history is carried
(in case any store checks it).
I opted to use the actual browser instance in case a Captcha was required, so I could solve it manually before the bot could loop indefinitely
(Terabyteshop asks the user to solve a Captcha only once in a session).

Even with all the workarounds, the loop may still fail for some unknown (to me) reason.
When this happens, a browser instance may be left open and blow up the memory if it repeats this behavior too much.
To address this I added a graceful exit procedure that, combined with a timeout method, allows the script to cleanly exit.
I also wrapped the python script execution with a shell script that loops restarting the process if it exits unexpectedly.

Finally, the bot also sends a "pulse" to slack (in a silenced channel) to indicate that it is still running.
I added this after I lost a chance to buy a card due to an uncaught timeout crash in the first day.

## Conclusion

This bot actually helped me buy the card I wanted for a fair price in 2020 :)
