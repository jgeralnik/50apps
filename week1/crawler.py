import sys
from lxml.html.clean import clean_html
from lxml.html.soupparser import fromstring
import requests
from Queue import Queue
from termcolor import colored
import argparse
import threading

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
    except LookupError:
      print "LookupError on", url
      return  #Content is in some unknown encoding
      
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

  def work():
    while True:
      url, depth = to_visit.get()
      visit(url, depth)
      to_visit.task_done()
      print "visited " + url

  for i in xrange(20):
    t = threading.Thread(target=work)
    t.daemon = True
    t.start()

  to_visit.put((url, depth))
  to_visit.join()
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Crawl the web for search query")
  parser.add_argument('url', help='The url to start the search from')
  parser.add_argument('query', help='The string to search for')
  parser.add_argument('-d', '--depth', type=int, help='The depth to search', default=1)
  args = parser.parse_args()
  for url in crawl(args.url,args.depth,args.query):
    print colored(url, 'red')
