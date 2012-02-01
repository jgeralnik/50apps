import sys
from lxml.html.clean import clean_html
from lxml.html.soupparser import fromstring
import requests
from Queue import Queue

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
      return #url is not valid

    if r.status_code != 200:
      return

    try:
      html = fromstring(r.content)
    except ValueError:
      return    #Content is not html

    html = clean_html(html)
    if search in html.text_content():
      result.add(url)

    if depth==0:
      return

    html.make_links_absolute(url)
    for element, attr, link, pos in html.iterlinks():
      to_visit.put((link, depth-1))


  to_visit.put((url, depth))
  while not to_visit.empty():
    url, depth = to_visit.get()
    visit(url, depth)
    print "visited " + url
  return result

if __name__ == "__main__":
  for url in crawl(sys.argv[1],int(sys.argv[2]), sys.argv[3]):
    print url
