import os
import pickle
import re
import time

from collections import OrderedDict
from datetime import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

BNF_SYMBOL = "BANKNIFTY"
NF_SYMBOL = "NIFTY"
STRIKE_PRICE_INDEX = 11
BNF_URL = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-9999&symbol=BANKNIFTY&symbol=BANKNIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"
NF_URL = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-10003&symbol=NIFTY&symbol=NIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"

value_time_pattern = re.compile(".*Underlying [a-zA-Z]+: [A-Z]+ (.*)  As on (.*)")
date_today = str(datetime.now().date())

def create_dir_if_not_exist(path):
    try:
        os.makedirs(path)
    except:
        pass

def parse_tr_for_elements(tr, tag_name="td"):
    sub_elements = tr.find_elements_by_tag_name(tag_name)
    return [tag.text for tag in sub_elements]

def get_oc_for_symbol(symbol, browser):
    print("Running for symbol: {}".format(symbol))
    browser.refresh()
    print("  Page loaded ...")
    trs = browser.find_elements_by_tag_name("tr")
    value, stime = value_time_pattern.findall(trs[0].text)[0]
    stime = str(datetime.strptime(stime, "%b %d, %Y %H:%M:%S %Z"))

    filepath = "/home/sandipan/trading/data/{}/{}".format(symbol, date_today)
    if not os.path.exists(filepath):
        create_dir_if_not_exist(os.path.dirname(filepath))
        octable = OrderedDict()
    else:
        with open(filepath, "r") as ocfile:
            octable = pickle.load(ocfile)

    octable[stime] = {"value": value, "oc": {}}
    for tr in trs[10:-7]:
        trdata = parse_tr_for_elements(tr)
        octable[stime]["oc"][int(float(trdata[STRIKE_PRICE_INDEX]))] = {
            "Call": {
                "OI": trdata[1],
                "ChangeInOI": trdata[2],
                "Volume": trdata[3],
                "IV": trdata[4],
                "LTP": trdata[5],
                "NetChange": trdata[6],
                "BidQty": trdata[7],
                "BidPrice": trdata[8],
                "AskPrice": trdata[9],
                "AskQty": trdata[10]
            },
            "Put": {
                "OI": trdata[21],
                "ChangeInOI": trdata[20],
                "Volume": trdata[19],
                "IV": trdata[18],
                "LTP": trdata[17],
                "NetChange": trdata[16],
                "BidQty": trdata[12],
                "BidPrice": trdata[13],
                "AskPrice": trdata[14],
                "AskQty": trdata[15]
            }
        }
    with open(filepath, "w") as ocfile:
        pickle.dump(octable, ocfile)

def get_browser_for_url(url):
    opts = Options()
    opts.set_headless()
    assert opts.headless
    try:
        browser = Firefox(options=opts)
        browser.get(url)
    except:
        print("Error initing browser. Sleeping before retrying ...")
        time.sleep(120)
        browser = Firefox(options=opts)
        browser.get(url)
    return browser

def main():
    while True:
        now = datetime.now()
        if (now.hour == 15 and now.minute >= 35) or now.hour > 15:
            print("Market closed. Exiting.")
            bnf_browser.close()
            nf_browser.close()
            break
        try:
            print("Running at {}".format(now))
            get_oc_for_symbol(BNF_SYMBOL, bnf_browser)
            get_oc_for_symbol(NF_SYMBOL, nf_browser)
        except Exception as e:
            print("Failed to fetch. Error: {}".format(e.message))
        print("Sleeping ...")
        time.sleep(300)

if __name__ == "__main__":
    print("Initing BNF Browser ...")
    bnf_browser = get_browser_for_url(BNF_URL)

    print("Initing NF Browser ...")
    nf_browser = get_browser_for_url(NF_URL)
    main()
