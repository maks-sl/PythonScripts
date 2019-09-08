import os
import json
from bs4 import BeautifulSoup
from _datetime import datetime
from time import time
import xml.dom.minidom
from time import sleep
import requests

APP_ID = 'eBayInc52-307e-4c8a-be3c-703469bb4s3'
FINDING_API_HEADERS = {
        "X-EBAY-SOA-SECURITY-APPNAME": APP_ID,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
    }

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILENAME = 'log.txt'
LAST_ERROR_PAGE_FILENAME = 'last-page-error.xml'
LAST_ERROR_PRODUCT_FILENAME = 'last-product-error.json'
GOOD_FILENAME = 'good.txt'
DLM = ':'
CHECKED_IDS_FILENAME = 'checked.txt'
EXCLUDED_SELLERS_FILENAME = 'excluded.txt'
TOKEN_FILENAME = 'token.txt'
# QUERY_TEXT = 'RTX 2080 TI'
QUERY_TEXT = 'macbook'
USE_EXISTING_DATA = True
PAGE_SIZE = 100
PRODUCT_REQUEST_DELAY = 0.0
TARGET_TO_CHECK = False
SORT_ORDERS = [
    'BestMatch',
    'CurrentPriceHighest',
    'StartTimeNewest',
    'EndTimeSoonest',
    'WatchCountDecreaseSort'
]
ITEM_FILTER_CONDITION = 1000
MIN_PRICE = 1000.00
BOX_INVENTORY = 0

_good, _bad, _unresolved = [], [], []
_existing_checked_ids, _ex_sellers, _process_checked_ids = [], [], []
_test_token_id, _current_token = None, None
_current_page, _total_parsed, _total_skipped = 1, 0, 0
_response_num_results = 0


def by_keywords_request(search_q, limit, sort, page=1):
    ep = 'https://svcs.ebay.com/services/search/FindingService/v1'
    ex_sellers = ''.join(map(lambda x: '<value>'+x+'</value>', _ex_sellers))
    xml_query = """<?xml version="1.0" encoding="UTF-8"?>
<findItemsByKeywordsRequest xmlns="http://www.ebay.com/marketplace/search/v1/services">
  <itemFilter>
    <name>Condition</name>
    <value>"""+str(ITEM_FILTER_CONDITION)+"""</value>
  </itemFilter>
  <itemFilter>
    <name>HideDuplicateItems</name>
    <value>1</value>
  </itemFilter>
  <itemFilter>
    <name>ValueBoxInventory</name>
    <value>"""+str(BOX_INVENTORY)+"""</value>
  </itemFilter>
  <itemFilter>
    <name>MinPrice</name>
    <value>"""+str(MIN_PRICE)+"""</value>
    <paramName>Currency</paramName>
    <paramValue>USD</paramValue>
  </itemFilter>
  <itemFilter>
    <name>ExcludeSeller</name>
    """+ex_sellers+"""
  </itemFilter>
  <sortOrder>"""+str(sort)+"""</sortOrder>
  <paginationInput>
    <entriesPerPage>"""+str(limit)+"""</entriesPerPage>
    <pageNumber>"""+str(page)+"""</pageNumber>
  </paginationInput>
  <keywords>"""+str(search_q)+"""</keywords>
</findItemsByKeywordsRequest>"""
    add = '?paginationInput.pageNumber='+str(page)+'&paginationInput.entriesPerPage='+str(limit)
    add2 = '?itemFilter(0).name=Condition&itemFilter(0).value=1000'
    # write_xml_to_file('qqq.xml', xml_query)
    return requests.post(ep, data=xml_query, headers=FINDING_API_HEADERS)


def product_request(p_id, token=False):
    global _current_token
    if not token:
        token = _current_token
    headers = {
        'User-Agent': 'eBayAndroid/5.13.0.14',
        'x-ebay-c-identity': 'id='+APP_ID+',idp=EBAYAPP',
        'x-ebay-c-marketplace-id': 'EBAY-US',
        'x-ebay-c-version': '1.0.0',
        'x-ebay-c-enduserctx': 'contextualLocation=country%3DUS',
        'x-ebay-c-exp': 'CHANNEL=4,noepheader=1',
        'Authorization': token,
        'Content-Type': 'application/xml; charset=UTF-8',
        'accept': 'application/json',
        'accept-language': 'en-US',
        'x-ebay-mobile-app-info': 'tz=0.00;ver=5.13.0.14',
    }
    end_point = 'https://apisd.ebay.com/buy/listing/v1/listingdetails/'
    end_point += str(p_id)
    end_point += '?inputoption=image.seller.avatar.200X200-jpg-l%2Creviewstats%2Cdescription%2Cfitmentsvc%2Csignals'
    end_point += '&fieldgroups=compact&fieldgroups=compatibility&fieldgroups=review'
    end_point += '&inputoption=richsnpt&fieldgroups=warranty&fieldgroups=vehicleHistoryReport'
    return requests.get(end_point, headers=headers)


def read_checked_ids():
    global _existing_checked_ids
    with open(make_abs_path(CHECKED_IDS_FILENAME), "r", encoding="utf-8") as file:
        _existing_checked_ids = file.read().splitlines()


def read_denied_users():
    global _ex_sellers
    with open(make_abs_path(EXCLUDED_SELLERS_FILENAME), "r", encoding="utf-8") as file:
        _ex_sellers = file.read().splitlines()


def log_text(text):
    with open(make_abs_path(LOG_FILENAME), 'a', encoding="utf-8") as error_file:
        error_file.write('['+str(f"{datetime.now():%Y-%m-%d_%H-%M-%S}")+']'+text+'\n')


def make_abs_path(filename):
    return os.path.join(CURRENT_PATH, filename)


def write_xml_to_file(filename, string_data):
    with open(make_abs_path(filename), 'w', encoding='utf-8') as file:
        xml_minidom = xml.dom.minidom.parseString(string_data)
        pretty_xml_as_string = xml_minidom.toprettyxml(encoding='utf-8')
        file.write(pretty_xml_as_string.decode("utf-8"))


def write_json_to_file(filename, json_data):
    with open(make_abs_path(filename), "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=1, sort_keys=True)


def write_text_to_file(filename, text_data):
    file_mode = 'a' if USE_EXISTING_DATA else 'w'
    with open(make_abs_path(filename), file_mode, encoding="utf-8") as file:
        file.write(text_data)


def print_time(header='TIMING'):
    print(str(header)+' : ' + str(f"{datetime.now():%Y-%m-%d_%H-%M-%S}"))


def print_msg(text, header='INFO'):
    msg_text = str(header) + ' : ' + str(text)
    # log_text(msg_text)
    print(msg_text)


def page_request(query_string, sort, page=1):
    global _current_page
    first_request = by_keywords_request(query_string, PAGE_SIZE, sort, page)
    xml_soup = BeautifulSoup(first_request.content, features='xml')

    ack = xml_soup.findItemsByKeywordsResponse.ack.contents[0]
    if not ack == 'Success':
        error_text = 'Ack not success at page '+str(_current_page)
        write_xml_to_file(LAST_ERROR_PAGE_FILENAME, first_request.content)
        raise Warning(error_text)
    total_entries = xml_soup.findItemsByKeywordsResponse.paginationOutput.totalEntries.contents[0]
    if int(total_entries) == 0:
        error_text = 'No results by query "' + query_string + '" at page '+str(_current_page)
        write_xml_to_file(LAST_ERROR_PAGE_FILENAME, first_request.content)
        raise Warning(error_text)

    print_msg('Page '+str(_current_page)+' request OK')
    return xml_soup


def check_valid_token(token):
    try:
        we_has_error = product_request(_test_token_id, token).json()['error_description']
        return False
    except KeyError:
        return True


def check_product_response(json_obj):
    global _current_token
    try:
        we_has_error = json_obj['error_description']
        write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, json_obj)
        we_wait_token = True
        while we_wait_token:
            print_msg('Token invalid', 'ERROR')
            new_token = input('New token required (also can "save" or "exit"): ')
            if new_token == 'save':
                return False
            if new_token == 'exit':
                print_msg('Cancelled by user. Exit.')
                exit()
            we_wait_token = not check_valid_token(new_token)
            if not we_wait_token:
                _current_token = new_token
                save_token_to_file()
                return True
    except KeyError:
        return True


def find_product_ship_methods(json_obj):
    result = []
    try:
        shipping_options = \
            json_obj['listing']['termsAndPolicies']['logisticsTerms']['logisticsPlan'][0]['steps'][0][
                'stepExtension']['shippingOption']
    except KeyError:
        # print_msg('Can not resolve shippingOptions.', 'WARNING')
        # write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, json_obj)
        return result

    shipping_methods = []
    for option in shipping_options:
        try:
            shipping_methods.append(option['shippingMethod'])
        except KeyError:
            pass
            # write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, json_obj)
            # print_msg('Can not resolve shippingMethod.', 'WARNING')

    for method in shipping_methods:
        try:
            result.append(method["shippingMethodCode"]['displayName']['content'])
        except KeyError:
            pass
            # write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, json_obj)
            # print_msg('Can not resolve displayName.', 'WARNING')

    return result


def find_product_purchase_options(json_obj):
    result = []
    try:
        purchase_options = json_obj['listing']['tradingSummary']['purchaseOptions']
    except KeyError:
        # print_msg('Can not resolve purchaseOptions.', 'WARNING')
        # write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, json_obj)
        return result
    for option in purchase_options:
        result.append(option)
    return result


def find_product_seller_name(json_obj):
    try:
        return json_obj['listing']['seller']['userIdentifier']['username']
    except KeyError:
        log_text('Can not find seller username.')
        return None


def resolve_products(items):
    global _good, _bad, _unresolved
    global _total_skipped, _total_parsed, _process_checked_ids, _existing_checked_ids
    for item in items:
        current_id = item.itemId.contents[0].strip()
        if current_id in _process_checked_ids or current_id in _existing_checked_ids:
            print_msg('[' + str(_total_parsed+1) + ']  Skip ID: ' + str(current_id))
            _total_skipped += 1
            continue
        sleep(PRODUCT_REQUEST_DELAY)
        print_msg('['+str(_current_page)+']['+str(_total_parsed+1)+'] Check ID: '+str(current_id))
        url = item.viewItemURL.contents[0]
        name = item.title.contents[0]

        product_json = product_request(current_id).json()
        # write_json_to_file(LAST_ERROR_PRODUCT_FILENAME, product_json)
        if not check_product_response(product_json):
            dump_all_data_and_exit()

        ship_methods = find_product_ship_methods(product_json)
        purchase_options = find_product_purchase_options(product_json)
        seller_name = find_product_seller_name(product_json)

        item_details = {
            'id': current_id,
            'name': name,
            'url': url,
            'seller_username': seller_name,
            'ship_methods': ship_methods,
            'parsed_at': time()
        }

        if 'BUY_IT_NOW' in purchase_options:
            if len(ship_methods) == 0:
                _unresolved.append(item_details)
            elif 'Fedex'.lower() in str(ship_methods).lower():
                _good.append(item_details)
                print_msg('GOOD PRODUCT FOUND! ID: '+current_id)
            else:
                _bad.append(item_details)
        else:
            print_msg('CAN NOT BUY IT NOW. ID: ' + current_id)
            _bad.append(item_details)

        _process_checked_ids.append(current_id)
        _total_parsed += 1
        if TARGET_TO_CHECK and TARGET_TO_CHECK <= _total_parsed:
            print_msg('Goal complete! '+str(_total_parsed)+' products checked.')
            dump_all_data_and_exit()


def read_token_and_test_id(xml_page):
    global _test_token_id, _current_token
    with open(make_abs_path(TOKEN_FILENAME), "r", encoding="utf-8") as last_token_file:
        _current_token = last_token_file.read().strip()
    _test_token_id = xml_page.findItemsByKeywordsResponse.searchResult.findAll("item")[0].itemId.contents[0].strip()


def save_results_to_files():
    global _good, _bad, _unresolved, _existing_checked_ids
    to_good, to_checked_ids = [], []
    for g in _good:
        to_good.append(DLM.join([g['id'], g['url']]))
        to_checked_ids.append(g['id'])
    for b in _bad:
        to_checked_ids.append(b['id'])
    for u in _unresolved:
        to_checked_ids.append(u['id'])
    if len(to_good) > 0:
        write_text_to_file(GOOD_FILENAME, '\n'.join(to_good)+'\n')
    if len(to_checked_ids) > 0:
        write_text_to_file(CHECKED_IDS_FILENAME, '\n'.join(to_checked_ids)+'\n')


def save_token_to_file():
    with open(make_abs_path(TOKEN_FILENAME), "w", encoding="utf-8") as token_file:
        token_file.write(_current_token)


def dump_all_data_and_exit():
    save_results_to_files()
    save_token_to_file()
    result_filename = 'total_' + f"{datetime.now():%Y-%m-%d_%H-%M-%S}" + '.json'
    total = {
        'queryString': QUERY_TEXT,
        'pageSize': PAGE_SIZE,
        'productsParsed': _total_parsed,
        'productsSkipped': _total_skipped,
        'initialResponseItems': _response_num_results,
        'totalGood': len(_good),
        'totalBad': len(_bad),
        'totalUnresolved': len(_unresolved),
        'useExistingData': str(USE_EXISTING_DATA),
        'numExistingIds': len(_existing_checked_ids),
    }
    write_json_to_file(result_filename, total)
    print_msg('Data saved! Exit.')
    exit()


def parse_page(xml_page):
    # write_xml_to_file('search-result.xml', str(xml_page))
    parsed_items = xml_page.findItemsByKeywordsResponse.searchResult.findAll("item")
    if len(parsed_items) == 0:
        print_msg('Not found items on page '+str(_current_page), 'ERROR')
        dump_all_data_and_exit()
    else:
        print_msg('Having '+str(len(parsed_items))+' products on page ' + str(_current_page)+'. Resolving...')
        resolve_products(parsed_items)
    print_msg('Page '+str(_current_page)+' parse OK')
    print_msg('Total parsed: '+str(_total_parsed))
    print_msg('Good found now: '+str(len(_good)))

if __name__ == "__main__":
    read_denied_users()
    try:
        initial_page_xml = page_request(QUERY_TEXT, SORT_ORDERS[0])
    except Warning as e:
        print_msg(str(e), 'INITIAL EXCEPTION')
        exit()
    _response_num_results = initial_page_xml.findItemsByKeywordsResponse.paginationOutput.totalEntries.contents[0]
    if len(_response_num_results) == 0:
        print_msg('Products by query "'+QUERY_TEXT+'" not found. Exit.')
        exit()
    answer = input('Found '+_response_num_results+' products. Continue? (y/n):')
    if not answer == 'y':
        print_msg('Cancelled by user. Exit.')
        exit()

    print_msg('Checker started. Query text: "'+QUERY_TEXT+'". '+_response_num_results+' products to check.')
    read_token_and_test_id(initial_page_xml)
    num_pages = int(initial_page_xml.findItemsByKeywordsResponse.paginationOutput.totalPages.contents[0])
    if USE_EXISTING_DATA:
        read_checked_ids()

    for sort_order in SORT_ORDERS if num_pages > 100 else SORT_ORDERS[:1]:
        print_msg('Next 100 pages SORTING: [' + sort_order + ']')
        for page_num in range(1, num_pages+1 if num_pages < 101 else 101):
            _current_page = page_num
            try:
                page_xml = page_request(QUERY_TEXT, sort_order, page_num)
            except Warning as e:
                print_msg(str(e), 'PAGE REQUEST EXCEPTION')
                dump_all_data_and_exit()
            parse_page(page_xml)
        print_msg('END THIS SORT. PARSED NOW: '+str(_total_parsed))

    print_msg('Success! ' + str(_total_parsed) + ' products checked.')
    dump_all_data_and_exit()
