import requests

option_chain_url = "https://www.nseindia.com/api/option-chain-{}?symbol={}"
equities_url = "https://www.nseindia.com/api/master-quote"
baseurl = "https://www.nseindia.com/"

def get_nse_response(url):
    headers = {
        "user-agent": "Chrome/80.0.3987.149 Safari/537.36",
        "accept-language": "en,gu;q=0.9,hi;q=0.8",
        "accept-encoding": "gzip, deflate, br",
    }
    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    return response.json()
