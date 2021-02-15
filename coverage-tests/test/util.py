import json
import os
import sys

import requests

# from jsonpath_ng import jsonpath
# from jsonpath_ng.ext import parse
from pip._vendor.retrying import retry

from applitools.common.utils import urlencode, urlsplit, urlunsplit


# @retry(exception=requests.HTTPError)
def get_test_info(api_key, results):
    api_session_url = results.api_urls.session
    r = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
        verify=False,
    )
    r.raise_for_status()
    return r.json()


def get_dom(results, dom_id):
    app_session_url = results.app_urls.session
    print("app_session_url = " + app_session_url)
    print("dom_id = " + dom_id)
    print(
        "APPLITOOLS_API_KEY_READ = " + str(os.getenv("APPLITOOLS_API_KEY_READ", None))
    )
    urlsplit_app_session_url = urlsplit(app_session_url)
    accountId = urlsplit_app_session_url.query
    url = urlunsplit(
        urlsplit_app_session_url._replace(
            path="/api/images/dom/" + dom_id + "/",
            query=accountId
            + "&"
            + urlencode(
                {
                    "apiKey": "SsEfrro4C1h0AJBhWkjDG9ZIM5IPZRG8WWMhdR1EMU4110",
                    "format": "json",
                }
            ),  # ({"apiKey": os.getenv("APPLITOOLS_API_KEY_READ", None), "format": "json"})
        )
    )
    res = requests.get(url)
    res.raise_for_status()
    orig = sys.stdout
    with open("filejson.txt", "w") as f:
        sys.stdout = f
        print(json.dumps(res.json(), indent=4, sort_keys=True))
        sys.stdout = orig
    return res.json()


def getNodesByAttribute(node, attribute):
    res = sum(
        (getNodesByAttribute(n, attribute) for n in node.get("childNodes", [])),
        [node] if attribute in node.get("attributes", {}) else [],
    )
    orig = sys.stdout
    with open("getNodesByAttribute22.txt", "w") as f:
        sys.stdout = f
        # print(json.dumps(jsonpath_expression.find(dom), indent=4, sort_keys=True))
        pretty2(res)
        # print("jsonpath_expression.find(dom) = " + str(res))
        sys.stdout = orig
    return res
    return sum(
        (getNodesByAttribute(n, attribute) for n in node.get("childNodes", [])),
        [node] if attribute in node.get("attributes", {}) else [],
    )


def pretty(d, indent=0):
    for x in range(len(d)):
        # print(str(x))
        for key, value in x.items():
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                pretty(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(value))


def pretty2(d):
    print(json.dumps(d, indent=4, sort_keys=True))


def getNodesByAttribute000(dom, attribute_name):
    result = []
    print("start getNodesByAttribute")
    # jsonpath_expression = parse('$..[?(@.attributes["' + attribute_name + '"])]')
    # jsonpath_expression = parse('$..[?(@.attributes["data-expected-frame"])]')

    # jsonpath_expression = parse('$..*[?attributes["' + attribute_name + '"]]')
    # jsonpath_expression = parse('$.childNodes[*].childNodes[?(@.attributes["data-expected-frame"])]')#"data-applitools-scroll")]')
    # jsonpath_expression = parse('$.childNodes[*].childNodes[?(@.attributes.data-expected-frame=="true")]')#"data-applitools-scroll")]')
    jsonpath_expression = parse(
        '$.childNodes[*].childNodes[*].childNodes[?(@.attributes.data-applitools-scroll=="true")]'
    )  # "data-applitools-scroll")]')

    # jsonpath_expression = parse('$..[[' + attribute_name + ']]')
    # if (dom["attributes"] is None): print("dom.get(attributes) != null")
    # else: print("dom[attributes] = " + str(dom["attributes"]))
    # if (dom["childNodes"] is None): print("dom.get(childNodes) != null")
    # else: print("dom[childNodes] = " + str(dom["childNodes"]))
    # jsonpath_expression = parse('$.[attributes]')
    # if (not dom["attributes"] is None) and (not dom["attributes"][attribute_name] is None):
    #   result.append(dom)
    #  return result
    # if dom["childNodes"]:
    #   for node in dom["childNodes"]: result.append(getNodesByAttribute(node, attribute_name))
    # return result
    # print("continue getNodesByAttribute")
    orig = sys.stdout
    with open("getNodesByAttribute.txt", "w") as f:
        sys.stdout = f
        # print(json.dumps(jsonpath_expression.find(dom), indent=4, sort_keys=True))
        print("jsonpath_expression.find(dom) = " + str(jsonpath_expression.find(dom)))
        sys.stdout = orig
    # print("jsonpath_expression.find(dom) = " + str(jsonpath_expression.find(dom)))
    # result.append(jsonpath_expression.find(dom))
    return jsonpath_expression.find(dom)
    # return dom['data-applitools-scroll']
