import sqlite3
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

class FirefoxDriver(object):
    def __init__(self):
        self.browser = webdriver.Firefox()

    def get_soup(self, url, wait_element=None):
        self.browser.get(url)
        html = self.browser.page_source
        if wait_element is not None:
            timeout = 10
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, wait_element))
                WebDriverWait(self.browser, timeout).until(element_present)
            except:
                print('unable to load webpage')
                return
        soup = BeautifulSoup(html, 'html.parser')
        return(soup)

    def close_out(self):
        self.browser.close()



# get a link to each story on the main page
def get_stories(browser, url):
    soup = browser.get_soup(url)
    stories = soup.find_all(class_="news-style1")
    story_data = []
    for story in stories:
        title = story.find(class_="floatleft").attrs['alt']
        category = story.find(class_="fblack bold news-ls05").text
        tags = story.find_all(class_="fblack")
        author = ''
        for tag in tags:
            if "news-ls05" not in tag.attrs['class']:
                author = tag.text
        link = story.find(class_="f22 fgrey4 bold").attrs['href']
        story_data.append((title, author, category, link))
    return story_data


# check each story for comments
def get_comments(browser, story_data):
    grabbed_comments = []
    for (title, author, category, link) in story_data:
        time.sleep(2)
        soup = browser.get_soup(link)
        comments = soup.find_all(class_="cmcont")
        count = 0
        for comment in comments:
            count += 1
            try:
                user = list(comment.find(class_="flag").next_siblings)[1].text
            except:
                user = ''
            try:
                country = comment.find(class_="flag").attrs['class'][1]
            except:
                country = ''
            try:
                score = comment.find(class_="pcp").text
            except:
                score = ''
            try:
                text = comment.find(class_="comtext").text.lstrip()
            except:
                text = ''
            try:
                comment_link = link + comment.find(title="Link to this comment").attrs['href']
            except:
                comment_link = ''
            grabbed_comments.append((user, country, score, text, title, author, category, link, comment_link))
            print(count, ' comment grabbed ', user, score)
    return grabbed_comments
# expand below threshold comments

# add comments to database
def add_comments_to_db(comments, db_name='PBComments', table_name='Comments'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ' + table_name + '(user text, country text, score text, comment_text text, title text, author text, category text, link text, comment_link text)')
    conn.commit()
    for (user, country, score, text, title, author, category, link, comment_link) in comments:
        c.execute('INSERT INTO ' + table_name + ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (user, country, score, text, title, author, category, link, comment_link))
        conn.commit()


if __name__ == "__main__":
    main_url = "https://www.pinkbike.com/"
    browser = FirefoxDriver()
    story_data = get_stories(browser, main_url)
    comments = get_comments(browser, story_data)
    browser.close_out()
    add_comments_to_db(comments)
