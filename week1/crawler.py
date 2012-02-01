import sys
from lxml.html.clean import clean_html
from lxml.html.soupparser import fromstring
import requests
from Queue import Queue
from termcolor import colored
import argparse

def crawl(url, depth, search):
  visited = set()
  to_visit = Queue()
  result = set()
  def visit(url, depth):
    if url in visited:
      return
    visited.add(url)

    try:
      r = requests.get(url)
    except ValueError:
      print "Url is invalid:", url 
      return #url is not valid
    except requests.exceptions.ConnectionError:
      print "Error connecting to", url
      return

    if r.status_code != 200:
      print "Status code is", r.status_code, "on", url
      return

    try:
      html = fromstring(r.content)
    except ValueError:
      print "ValueError on", url
      return    #Content is not html
      
    except TypeError:
      print "TypeError on", url 
      return    #Content is not html

    html = clean_html(html)
    if search.lower() in html.text_content().lower():
      result.add(url)

    if depth==0:
      return

    html.make_links_absolute(url)
    for element, attr, link, pos in html.iterlinks():
      if attr == "href":
        to_visit.put((link, depth-1))


  to_visit.put((url, depth))
  while not to_visit.empty():
    url, depth = to_visit.get()
    visit(url, depth)
    print "visited " + url
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Crawl the web for search query")
  parser.add_argument('url', help='The url to start the search from')
  parser.add_argument('query', help='The string to search for')
  parser.add_argument('-d', '--depth', type=int, help='The depth to search', default=1)
  args = parser.parse_args()
  for url in crawl(args.url,args.depth,args.query):
    print colored(url, 'red')
