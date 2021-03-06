# pylint: disable=import-error
import VM_OrchestratorApp.src.utils.mongo as mongo

import base64
import os
import shutil
import subprocess

def start_aquatone(subdomain_list, scan_information):

    # Subdomains are already alive
    # We need to put the subdomains into a text file for feeding it into aquatone

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = ROOT_DIR + '/output'
    if not os.path.exists(OUTPUT_DIR + '/aquatone'):
        os.makedirs(OUTPUT_DIR + '/aquatone')

    OUTPUT_DIR = ROOT_DIR + '/output' + '/aquatone'
    INPUT_DIR = OUTPUT_DIR + '/aquatone_input.txt'
    AQUATONE_DIR = ROOT_DIR + '/tools/aquatone'

    print('Aquatone starting against ' + str(len(subdomain_list)) + ' subdomains')
    for subdomain in subdomain_list:
        run_aquatone(subdomain['subdomain'], AQUATONE_DIR, OUTPUT_DIR)

    cleanup(OUTPUT_DIR)

    return

def run_aquatone(subdomain, AQUATONE_DIR, OUTPUT_DIR):

    command = ['echo', subdomain, '|', AQUATONE_DIR, '-ports', 'large', '-out', OUTPUT_DIR]
    subprocess.run(
       ' '.join(command), shell=True)

    # Parsing de resultados
    parse_results(subdomain, OUTPUT_DIR)
    # Cleanup
    cleanup_after_scan(OUTPUT_DIR)

    return

def parse_results(subdomain, OUTPUT_DIR):

    urls = list()
    # Check if we have http and https
    try:
        with open(OUTPUT_DIR + '/aquatone_urls.txt') as fp:
            lines = fp.read()
            urls = lines.split('\n')
    except FileNotFoundError:
        print('ERROR: Auatone urls file was not found')
        pass

    urls_to_add = list()
    urls = [string for string in urls if string != ""]
    if urls and urls != ['']:
        for url in urls:
            urls_to_add.append({'url': url})
        has_urls = True
    else:
        urls_to_add = None
        has_urls = False

    http_image_string = ''
    https_image_string = ''
    image_files = os.listdir(OUTPUT_DIR + '/screenshots')
    if image_files:
        for image in image_files:
            if 'http__' in image:
                with open(OUTPUT_DIR + '/screenshots/' + image, "rb") as image_file:
                    http_image_string = base64.b64encode(image_file.read())
            if 'https__' in image:
                with open(OUTPUT_DIR + '/screenshots/' + image, "rb") as image_file:
                    https_image_string = base64.b64encode(image_file.read())

    mongo.add_urls_from_aquatone(subdomain, has_urls, urls_to_add)
    mongo.add_images_to_subdomain(subdomain, http_image_string, https_image_string)

    return

def cleanup_after_scan(OUTPUT_DIR):
    try:
        os.remove(OUTPUT_DIR + '/aquatone_report.html')
    except FileNotFoundError:
        pass
    try:
        os.remove(OUTPUT_DIR + '/aquatone_session.json')
    except FileNotFoundError:
        pass
    try:
        os.remove(OUTPUT_DIR + '/aquatone_urls.txt')
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(OUTPUT_DIR + '/headers')
    except OSError:
        pass
    try:
        shutil.rmtree(OUTPUT_DIR + '/html')
    except OSError:
        pass
    try:
        shutil.rmtree(OUTPUT_DIR + '/screenshots')
    except OSError:
        pass

    return

def cleanup(OUTPUT_DIR):

    try:
        shutil.rmtree(OUTPUT_DIR)
    except OSError:
        pass
    return
