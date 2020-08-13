import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def getRandomPage(page='https://en.wikipedia.org/wiki/Special:Random'):
    html = requests.get(page).text 
    soup = BeautifulSoup(html, 'lxml')
    return soup

def getTitle(page):
    try:
        title = page.find("h1", {'id':'section_0'}).text
    except:
        title = page.find("h1", {'id': 'firstHeading'}).text

    return title

def parenText(text): #Finds text between parentheses
    textList = list(str(text))
    parsed = ''
    parens = 0
    startOfParen = False
    endOfParen = False

    for index, char in enumerate(str(text)):
        if char == '(':
            if parens == 0:
                start = index
                startOfParen = True
            parens+=1
            continue

        elif char == ')':
            parens-=1
            if parens ==0:
                end = index
                endOfParen = True

        if startOfParen == True and endOfParen == True:
            capturedString=''.join(textList[start:end+1]) #Converts the list into a string
            if '<a' in capturedString: #Checks if captured string contains a link
                parsed = parsed + capturedString
            startOfParen = False
            endOfParen = False
            continue

    return parsed


def removeLinks(firstParagraph): #Removes links from the parentheses text
    links = firstParagraph.find_all('a')
    goodLinks = []
    badLinkText = parenText(str(firstParagraph))
    parenLinks = parenText(firstParagraph)
    goodLinks = [links[i]['href'] for i in range(len(links))
                 if str(links[i]) not in badLinkText and '.ogg' not in links[i]['href']]

    return goodLinks


def removeElements(body, classes, *element):
    if len(element) > 0:
        for div in body.find_all(element, classes):
            div.decompose() #Decompose recursively removes elements from the DOM tree and their associations
    else:
        for div in body.find_all(classes):
            div.decompose()


def getNextLink(page):
    body = page.find("div", {'id':'mw-content-text'}) #Get the main body text

    removeElements(body, {'class': ['toc', 'toc-mobile'], 'id': 'toc'}, 'div',) #Remove table of contents
    removeElements(body, {'role': 'navigation'}, 'div' )  # Remove navigation boxes
    removeElements(body, {'class': ['new', 'external free', 'external text', 'extiw']},'a') #Remove external links
    removeElements(body, {'class': ['mw-editsection', 'IPA', 'IPA nopopups', 'nowrap']}, 'span') #Remove IPA and edit spans
    removeElements(body, {'class': 'metadata'}, 'small') #Remove metadata links
    removeElements(body, ['table', 'i', 'sup', 'img']) #Remove tables, italics, superscripts

    paragraphs = body.findChildren(['p','ul','li'])
    paraIndex = 0
    firstParagraph = paragraphs[paraIndex]
    goodLinks = removeLinks(firstParagraph)

    try:
        while goodLinks == []: #grabs the next paragraph if the first contains no valid links
            firstParagraph = paragraphs[paraIndex+1]
            goodLinks = removeLinks(firstParagraph)
            paraIndex+=1
    except: #expand link search if no valid links found in any paragraph
        goodLinks = removeLinks(body)

    if goodLinks is not None:
        nextLink = urljoin('https://en.wikipedia.org', goodLinks[0])
        return nextLink
    else:
        raise TypeError('404/No Good Links Found ')


def goToNext(page):
    try:
        nextPage=getNextLink(page)
        print(nextPage)
        html = requests.get(nextPage).text
        soup = BeautifulSoup(html, 'lxml')
        return soup
    except:
        raise TypeError('404/No Good Links Found ')


if __name__ == '__main__':
    
    page = input("please Write wiki link : ")   
    if "https://en.wikipedia.org" not in page:
        print("I'll use random wiki page ")
        page = getRandomPage()
    else:
        page = getRandomPage(page)
    while True:
        title = getTitle(page)
        if title == 'Philosophy':
            print("Job Done!")
            break
        page = goToNext(page)
        time.sleep(0.5)