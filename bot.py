import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from random import randint, uniform as randfloat
import signal
from contextlib import contextmanager
import urllib3
import json
from fake_useragent import UserAgent

WEBHOOK_ALERT = os.environ.get("WEBHOOK_ALERT")
WEBHOOK_PULSE = os.environ.get("WEBHOOK_PULSE")

if not WEBHOOK_ALERT or len(WEBHOOK_ALERT) == 0:
    print("ALERT WEBHOOK NOT CONFIGURED!")
if not WEBHOOK_PULSE or len(WEBHOOK_PULSE) == 0:
    print("PULSE WEBHOOK NOT CONFIGURED!")


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        raise TimeoutError
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


def send_message(message, alert=True):
    # print to stdout
    print(message)
    # skip messaging if not configured
    if (
        not WEBHOOK_PULSE
        or not WEBHOOK_ALERT
        or len(WEBHOOK_PULSE) == 0
        or len(WEBHOOK_ALERT) == 0
    ):
        return

    global last_pulse

    if alert:
        url = WEBHOOK_ALERT
    # send a pulse every minute
    elif last_pulse is None or time.time() - last_pulse > 60:
        url = WEBHOOK_PULSE
        last_pulse = time.time()
    else:
        return

    # NOTE: update body to match what the webhook expects
    # (e.g. slack uses "text" and discord uses "content")
    encoded_body = json.dumps({"content": message}).encode("utf-8")
    http = urllib3.PoolManager()
    http.request(
        "POST",
        url,
        body=encoded_body,
        headers={"Content-Type": "application/json"},
    )


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
# NOTE: update the driver to match the browser you have installed
driver = webdriver.Chrome("./chromedriver", options=options)
# NOTE: update what you are looking for
pages = {
    "tickets": {
        "url": "https://www.eventim.com.br/event/arctic-monkeys-jeunesse-arena-15252258/",
        "method": driver.find_element_by_css_selector,
        "arg": 'div[data-cc-formcount="1_2_tickets"] div[data-tt-name="MEIA ENTRADA"] .ticket-type-stepper',
    },
}
keys = list(pages.keys())
page = randint(0, len(pages) - 1)
userAgent = UserAgent()
last_pulse = None
send_message("Starting...", alert=False)
# play a sound to enable OS audio source selection
while True:
    print()
    print(time.ctime())
    time_wait = randfloat(10, 20)

    # change userAgent every request
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {"userAgent": userAgent.random},
    )
    # driver.get("https://www.httpbin.org/headers")  # test header update
    try:
        with timeout(60):
            send_message("Checking {}".format(keys[page]), alert=False)
            # access page
            driver.get(pages[keys[page]]["url"])
            # test
            pages[keys[page]]["method"](pages[keys[page]]["arg"])
            # if there was no exception, the element was found!
            send_message(
                "{} found!!! {}".format(
                    keys[page].capitalize(), pages[keys[page]]["url"]
                )
            )
    except NoSuchElementException:
        print("Element not found!")
        try:
            if driver.find_element_by_xpath(
                "//h1 [contains( text(), 'Access Denied')]"
            ):
                print("Resetting the browser after access denied.")
                exit(1)
        except NoSuchElementException:
            pass
    except Exception as e:
        print("Unknown exception:", e)
        try:
            driver.close()
        except:
            pass
        try:
            driver.quit()
        except:
            pass
        exit(1)

    print("Sleeping {} seconds...".format(time_wait))
    time.sleep(time_wait)
    page = (page + 1) % len(pages)
