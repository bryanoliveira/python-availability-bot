import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from random import randint, uniform as randfloat
from playsound import playsound
import signal
from contextlib import contextmanager
import urllib3
import json
from mss import mss
from fake_useragent import UserAgent

SLACK_ALERT_WEBHOOK = os.environ.get("SLACK_ALERT_WEBHOOK")
SLACK_PULSE_WEBHOOK = os.environ.get("SLACK_PULSE_WEBHOOK")

if len(SLACK_ALERT_WEBHOOK) == 0:
    print("SLACK ALERT HOOK NOT CONFIGURED!")
if len(SLACK_PULSE_WEBHOOK) == 0:
    print("SLACK PULSE HOOK NOT CONFIGURED!")

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
    # skip slack messaging if not configured
    if len(SLACK_PULSE_WEBHOOK) == 0 or len(SLACK_ALERT_WEBHOOK) == 0:
        return

    global last_pulse

    if alert:
        url = SLACK_ALERT_WEBHOOK
    # send a pulse every minute
    elif last_pulse is None or time.time() - last_pulse > 60:
        url = SLACK_PULSE_WEBHOOK
        last_pulse = time.time()
    else:
        return

    encoded_body = json.dumps({"text": message}).encode("utf-8")
    http = urllib3.PoolManager()
    http.request(
        "POST", url, body=encoded_body, headers={"Content-Type": "application/json"},
    )


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome("./chromedriver-86-linux", options=options)
pages = {
    "3070 at terabyte": {
        "url": "https://www.terabyteshop.com.br/busca?str=rtx+3070",
        "method": driver.find_element_by_class_name,
        "arg": "bt-cmp",
    },
    "3080 at terabyte": {
        "url": "https://www.terabyteshop.com.br/busca?str=rtx+3080",
        "method": driver.find_element_by_class_name,
        "arg": "bt-cmp",
    },
    "3070 at kabum": {
        "url": "https://www.kabum.com.br/cgi-local/site/listagem/listagem.cgi?string=rtx3070&btnG=",
        "method": driver.find_element_by_xpath,
        "arg": "//img[contains(@src,'https://static.kabum.com.br/conteudo/temas/001/imagens/icones/comprar.png')]",
    },
    "3080 at kabum": {
        "url": "https://www.kabum.com.br/cgi-local/site/listagem/listagem.cgi?string=rtx+3080&btnG=",
        "method": driver.find_element_by_xpath,
        "arg": "//img[contains(@src,'https://static.kabum.com.br/conteudo/temas/001/imagens/icones/comprar.png')]",
    },
    "3070 & 3080 at pichau": {
        "url": "https://www.pichau.com.br/hardware/placa-de-video?amp%3Bproduct_list_limit=48&amp%3Bproduct_list_order=name&rgpu=6304%2C6305",
        "method": driver.find_element_by_class_name,
        "arg": "tocart",
    },
}
keys = list(pages.keys())
page = randint(0, len(pages) - 1)
userAgent = UserAgent()
last_pulse = None
send_message("Starting...", alert=False)
# play a sound to enable OS audio source selection
playsound("3.mp3")
while True:
    print()
    print(time.ctime())

    # change userAgent every request
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride", {"userAgent": userAgent.random},
    )
    # driver.get("https://www.httpbin.org/headers")  # test header update
    try:
        with timeout(60):
            send_message("Checking {}".format(keys[page]), alert=False)
            # access page
            driver.get(pages[keys[page]]["url"])
            # test
            pages[keys[page]]["method"](pages[keys[page]]["arg"])
            # if there was no exception, the button was found!
            send_message("{} found!!!".format(keys[page]))
            with mss() as sct:
                sct.shot(
                    mon=-1, output="prints/{} - {}.png".format(time.ctime(), keys[page])
                )
            playsound("1.mp3")
            playsound("2.mp3")
            playsound("3.mp3")
    except NoSuchElementException:
        s = randfloat(10, 35)
        print("Dit not found! Sleeping {} seconds...".format(s))
        time.sleep(s)
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
        exit()

    page = (page + 1) % len(pages)

