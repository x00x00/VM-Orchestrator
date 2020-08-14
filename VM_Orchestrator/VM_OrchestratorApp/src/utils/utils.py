# pylint: disable=import-error
import requests
import re
import math
import os
import subprocess
import traceback
from urllib.parse import urlparse
import VM_OrchestratorApp.src.constants as c
from VM_Orchestrator.settings import settings
from selenium import webdriver

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

regex_str = r"""
          (?:"|')                               # Start newline delimiter
          (
            ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
            [^"'/]{1,}\.                        # Match a domainname (any character + dot)
            [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
            |
            ((?:/|\.\./|\./)                    # Start with /,../,./
            [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
            [^"'><,;|()]{1,})                   # Rest of the characters can't be
            |
            ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
            [a-zA-Z0-9_\-/]{1,}                 # Resource name
            \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
            (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters
            |
            ([a-zA-Z0-9_\-/]{1,}/               # REST API (no extension) with /
            [a-zA-Z0-9_\-/]{3,}                 # Proper REST endpoints usually have 3+ chars
            (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters
            |
            ([a-zA-Z0-9_\-]{1,}                 # filename
            \.(?:php|asp|aspx|jsp|json|
                 action|html|js|txt|xml)        # . + extension
            (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters
          )
          (?:"|')                               # End newline delimiter
        """

def get_response(url):
    try:
        response = requests.get(url, verify=False, timeout=3)
    except requests.exceptions.SSLError:
        print('Url %s raised SSL Error at utils.py' % url)
        return None
    except requests.exceptions.ConnectionError:
        print('Url %s raised Connection Error at utils.py' % url)
        return None
    except requests.exceptions.ReadTimeout:
        print('Url %s raised Read Timeout Error at utils.py' % url)
        return None
    except requests.exceptions.TooManyRedirects:
        print('Url %s raised Too many redirects Error at utils.py' % url)
        return None
    except Exception:
        error_string = traceback.format_exc()
        final_error = 'On {0}, was Found: {1}'.format(url,error_string)
        print(final_error)
        return None
    return response

def get_js_files(url):
    js_files = list()
    regex = re.compile(regex_str, re.VERBOSE)
    response = get_response(url)
    if response is None:
        return []
    all_matches = [(m.group(1), m.start(0), m.end(0)) for m in re.finditer(regex, response.text)]
    for match in all_matches:
        url = match[0]
        http_js = ['.js', 'http://']
        https_js = ['.js', 'https://']
        if all(substring in url for substring in http_js):
            js_files.append(url)
        if all(substring in url for substring in https_js):
            js_files.append(url)
    return js_files


def get_css_files(url):
    css_files = list()
    regex = re.compile(regex_str, re.VERBOSE)
    response = get_response(url)
    if response is None:
        return []
    all_matches = [(m.group(1), m.start(0), m.end(0)) for m in re.finditer(regex, response.text)]
    for match in all_matches:
        url = match[0]
        http_css = ['.css', 'http://']
        https_css = ['.css', 'https://']
        if all(substring in url for substring in http_css):
            css_files.append(url)
        if all(substring in url for substring in https_css):
            css_files.append(url)
    return css_files


def url_screenshot(url):
    global ROOT_DIR
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox') #Sino pongo esto rompe
    options.add_argument('--headless') #no cargue la ventana (background)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920,1080)
    driver.get(url)
    name = url.replace("http://","").replace("https://","").split("/")[0]
    OUTPUT_DIR = ROOT_DIR+'/../security/tools_output'
    driver.save_screenshot(OUTPUT_DIR+name+".png")
    driver.quit()

# Receives url_list = [{'url': url}]
def get_distinct_urls(url_list):
    parsed_urls = list()
    #We will add each url netloc to a list, then we will return geturl() of each one
    for url in url_list:
        url_parse = urlparse(url['url'])
        found = False
        for sub_url in parsed_urls:
            if url_parse.netloc == sub_url.netloc:
                found = True
                break
        if not found:
            parsed_urls.append(url_parse)

    final_url_list = list()
    for url in parsed_urls:
        final_url_list.append(url.geturl())

    return final_url_list

def get_web_function_by_name(web_vuln):
    # We will create a list with all our valid web vulns dictionaries for comparisson
    # c is our constants file. We will not re-run vulns that require verification for now
    vuln_names = [c.INVALID_VALUE_ON_HEADER, c.HEADER_NOT_FOUND,
    c.HOST_HEADER_ATTACK, c.UNSECURE_METHOD, c.SSL_TLS, c.OUTDATED_3RD_LIBRARIES,
    c.CORS, c.ENDPOINT, c.BUCKET, c.TOKEN_SENSITIVE_INFO, c.CSS_INJECTION,
    c.OPEN_FIREBASE, c.IIS_SHORTNAME_MICROSOFT, c.POSSIBLE_ERROR_PAGES]

    language_key = 'english_name'
    if settings['LANGUAGE'] == 'spa':
        language_key = 'spanish_name'

    for name in vuln_names:
        if web_vuln['vulnerability_name'] == name[language_key]:
            return name['task']
    return None

def get_infra_function_by_name(infra_vuln):
    vuln_names = [c.OUTDATED_SOFTWARE_NMAP, c.HTTP_PASSWD_NMAP, c.WEB_VERSIONS_NMAP, c.ANON_ACCESS_FTP, 
    c.CRED_ACCESS_FTP, c.DEFAULT_CREDS, c.PLAINTEXT_COMUNICATION, c.UNNECESSARY_SERVICES]
    
    language_key = 'english_name'
    if settings['LANGUAGE'] == 'spa':
        language_key = 'spanish_name'

    for name in vuln_names:
        if infra_vuln['vulnerability_name'] == name[language_key]:
            return name['task']
    return None

