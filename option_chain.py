import pickle
import re
import signal
import sys
import time

from collections import OrderedDict
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from utils import *

BNF_SYMBOL = "BANKNIFTY"
NF_SYMBOL = "NIFTY"
STRIKE_PRICE_INDEX = 11
OC_BASE_URL = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?segmentLink=17"
INDEX_URL = OC_BASE_URL + "&instrument=OPTIDX&symbol={}"
STOCK_URL = OC_BASE_URL + "&instrument=OPTSTK&symbol={}"
MONTHLY_EXPIRY_SUFFIX = "&date={}"
INDIA_VIX_URL = "https://in.investing.com/indices/india-vix"

value_time_pattern = re.compile(".*Underlying [a-zA-Z]+: [A-Z]+ ([0-9.]+)  As on (.*)")
date_today = datetime.now().date()

def parse_tr_for_elements(tr, tag_name="td"):
    sub_elements = tr.find_elements_by_tag_name(tag_name)
    return [tag.text for tag in sub_elements]

def compute_max_pain(trs):
    print("  Computing Max Pain ...", end="")
    all_expiry_loss = {}
    for index, exp_trdata in enumerate(trs):
        exp_strike_price = int(float(exp_trdata[STRIKE_PRICE_INDEX]))
        expiry_loss = 0
        for trdata in trs:
            strike_price = int(float(trdata[STRIKE_PRICE_INDEX]))
            call_oi = int(trdata[1].replace(",", "").replace("-", "0"))
            put_oi = int(trdata[21].replace(",", "").replace("-", "0"))
            if strike_price == exp_strike_price:
                continue
            elif strike_price > exp_strike_price:
                expiry_loss += abs(strike_price - exp_strike_price) * put_oi
            else:
                expiry_loss += abs(strike_price - exp_strike_price) * call_oi
        all_expiry_loss[exp_strike_price] = expiry_loss
    max_pain = min(list(all_expiry_loss.keys()), key=all_expiry_loss.get)
    print(max_pain)
    return max_pain

def get_oc_for_symbol(symbol, browser, india_vix_value, expiry_date, monthly=False):
    print("Running {} for symbol: {}".format("monthly" if monthly else "weekly", symbol))
    print("  Reloading page ...")
    browser.refresh()

    trs = browser.find_elements_by_tag_name("tr")
    value, stime = value_time_pattern.findall(trs[0].text)[0]
    total_oi_line = trs[-2].text.split(" ")
    pcr_ratio = float(total_oi_line[-2].replace(",", "")) / float(total_oi_line[1].replace(",", ""))
    stime = str(datetime.strptime(stime, "%b %d, %Y %H:%M:%S %Z"))
    print("  PCR: {}".format(pcr_ratio))

    print("  Parsing oc table ...")
    trs = [parse_tr_for_elements(tr) for tr in trs[10:-7]]

    filepath = "{}/trool/data/{}/{}/{}".format(get_home_directory(), symbol, "monthly" if monthly else "weekly", expiry_date)
    if not os.path.exists(filepath):
        create_dir_if_not_exist(os.path.dirname(filepath))
        octable = OrderedDict()
    else:
        with open(filepath, "rb") as ocfile:
            octable = pickle.load(ocfile)

    octable[stime] = {
        "value": value,
        "india_vix": india_vix_value,
        "max_pain": compute_max_pain(trs),
        "pcr": round(pcr_ratio, 2),
        "oc": {}}
    for trdata in trs:
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
    with open(filepath, "wb") as ocfile:
        pickle.dump(octable, ocfile)

def get_browser_for_url(url):
    opts = Options()
    opts.headless = True
    try:
        browser = Firefox(options=opts)
        browser.get(url)
    except:
        print("Error initing browser. Sleeping before retrying ...")
        time.sleep(120)
        browser = Firefox(options=opts)
        browser.get(url)
    return browser

def cleanup(signal=None, frame=None):
    print("Closing open browser sessions before exit ...")
    try:
        bnf_weekly_browser.close()
        nf_weekly_browser.close()
        bnf_monthly_browser.close()
        nf_monthly_browser.close()
        india_vix_browser.close()
    except:
        pass
    sys.exit()

def get_value_for_india_vix():
    india_vix_browser.refresh()
    return india_vix_browser.find_element_by_id("last_last").text

def main():
    while True:
        now = datetime.now()
        if is_market_closed():
            print("Market closed. Exiting.")
            break
        try:
            print("Running at {}".format(now))
            india_vix_value = get_value_for_india_vix()
            get_oc_for_symbol(BNF_SYMBOL, bnf_monthly_browser, india_vix_value, monthly_expiry_date, monthly=True)
            get_oc_for_symbol(NF_SYMBOL, nf_monthly_browser, india_vix_value, monthly_expiry_date, monthly=True)

            if not is_expiry_week:
                get_oc_for_symbol(BNF_SYMBOL, bnf_weekly_browser, india_vix_value, weekly_expiry_date)
                get_oc_for_symbol(NF_SYMBOL, nf_weekly_browser, india_vix_value, weekly_expiry_date)
        except Exception as e:
            print("Failed to fetch. Error: {}".format(e))
        print("Sleeping ...")
        time.sleep(180)

if __name__ == "__main__":
    if is_market_closed():
        print("Market closed. Exiting.")
        sys.exit()
    signal.signal(signal.SIGINT, cleanup)
    monthly_expiry_date = get_expiry_date()
    is_expiry_week = False
    if int(monthly_expiry_date[:2]) < date_today.day:
        # This month's expiry date has passed. Should pick next month's.
        monthly_expiry_date = get_expiry_date(date_today.year, date_today.month + 1)
    elif (int(monthly_expiry_date[:2]) - date_today.day) < 7:
        # This is expiry week. No need to fetch for two separate dates.
        print("Is expiry week. Will skip fetching weekly option chain.")
        is_expiry_week = True

    print("Initing monthly BNF Browser ...")
    bnf_monthly_browser = get_browser_for_url(INDEX_URL.format(BNF_SYMBOL) + MONTHLY_EXPIRY_SUFFIX.format(monthly_expiry_date))
    print("Initing monthly NF Browser ...")
    nf_monthly_browser = get_browser_for_url(INDEX_URL.format(NF_SYMBOL) + MONTHLY_EXPIRY_SUFFIX.format(monthly_expiry_date))

    if not is_expiry_week:
        print("Initing weekly BNF Browser ...")
        bnf_weekly_browser = get_browser_for_url(INDEX_URL.format(BNF_SYMBOL))
        print("Initing weekly NF Browser ...")
        nf_weekly_browser = get_browser_for_url(INDEX_URL.format(NF_SYMBOL))
        weekly_expiry_date = bnf_weekly_browser.find_element_by_id("date").text.split("\n")[1]
    print("Fetching value for india vix ...")
    india_vix_browser = get_browser_for_url(INDIA_VIX_URL)
    main()
    cleanup()
