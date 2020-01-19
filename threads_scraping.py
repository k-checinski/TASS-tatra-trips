from bs4 import BeautifulSoup
import json
import os
import requests
import time

forum_url = 'http://gorybezgranic.pl/'


def exact_thread_id(url: str):
    begin = url.find('-vt') + 3
    end = url.find('.htm')
    return url[begin:end]


def scrap_forum_page(url: str):
    req = requests.get(url)
    req.encoding = 'iso-8859-2'
    soup = BeautifulSoup(req.text, features='html.parser')
    threads_table = soup.find_all('table')[2]
    rows = threads_table.find_all('tr')[1:]
    threads = list()
    for row in rows:
        thread = dict()
        cells = row.find_all('td')
        if len(cells) < 7:
            break
        thread['title'] = cells[2].find('a').text
        thread['url'] = exact_thread_id(cells[2].find('a')['href'])
        thread['author'] = cells[4].find('br').text
        thread['date'] = cells[4].find('span', 'gensmall').text
        thread['answers_num'] = int(cells[3].text)
        thread['views_num'] = int(cells[5].text)
        threads.append(thread)
    return threads


def scrap_forum(url: str, max_pages=50, sleep=2):
    threads = list()
    for i in range(max_pages):
        print(F'Scraping page {i}')
        page_url = url.format(i * 25)
        new_threads = scrap_forum_page(page_url)
        print(F'Sleeping for {sleep} second(s)')
        time.sleep(sleep)
        if len(new_threads) == 0:
            break
        print(F'{len(new_threads)} thread(s) scraped')
        threads += new_threads
    return threads


def scrap_thread_page(url: str):
    req = requests.get(url)
    req.encoding = 'iso-8859-2'
    soup = BeautifulSoup(req.text, features='html.parser')
    table = soup.find('table', 'forumline')
    rows = table.find_all('tr', recursive=False)
    answer_rows = [rows[i] for i in range(2, len(rows), 3)]
    answers = list()
    for row in answer_rows:
        answer = dict()
        cells = row.find_all('td', recursive=False)
        author = dict()
        author_name = cells[0].find('a', title='Zobacz profil autora')
        if author_name is None:
            break
        author['name'] = cells[0].find('a', title='Zobacz profil autora').text
        details = str(cells[0].find('span', 'postdetails')).split('<br')
        posts = [d for d in details if d.find('Posty') != -1][0]
        author['posts'] = int(''.join(c for c in posts if c.isdigit()))
        answer['author'] = author
        answer['content'] = cells[1].find('table').find_all('tr')[2].text
        answers.append(answer)
    return answers


def scrap_thread(thread_id: str, max_pages=20, sleep=2):
    page_url = forum_url + '-vt' + thread_id + ',{}.htm'
    answers = list()
    for i in range(max_pages):
        print(F'Scraping page {i}')
        curr_page_url = page_url.format(i * 15)
        print(curr_page_url)
        new_answers = scrap_thread_page(curr_page_url)
        if len(new_answers) == 0:
            break
        print(F'Sleeping for {sleep} second(s)')
        time.sleep(sleep)
        print(F'{len(new_answers)} answer(s) scraped')
        answers += new_answers
    return answers


def scrap_all_threads(threads, out_dir):
    for i, thread in enumerate(threads):
        content = dict()
        content['thread_info'] = thread
        content['answers'] = scrap_thread(thread['url'])
        print('THREAD ', thread['url'])
        with open(os.path.join(out_dir, F'{i}_{thread["url"]}.json'), 'w+') as file:
            json.dump(content, file)