import requests
import re
from bs4 import BeautifulSoup
import json
import os

class Scraper:
    page = False
    soup = False

    def __init__(self):
        pass

    def open(self, url):
        """
            Opens the URL using the requests module and creates a
            beautifulsoup instance.
        """
        try:
            self.page = requests.get(url, timeout=15)
            self.soup = BeautifulSoup(self.page.content, "html.parser")
        except Exception as e:
            print(e)

    def external_links(self):
        """
            Cycles through all tags on the page and checks for a 'src'
            or a 'href' attribute. Ignores all links that start with '/'
            and '#' and any links that match the regex.

            Returns a list of all resources as dicts.
        """
        resources = []
        cfc_url = re.compile("(([a-z0-9]+).)?cfcunderwriting+(.{1}([a-z]+))")

        if not self.soup or not self.page:
            return resources

        tags = {tag.name for tag in self.soup.find_all()}

        for tag in tags:
            for i in self.soup.find_all(tag):
                res = {}
                if i.has_attr("href"):
                    res["type"] = i.name
                    res["resource"] = i["href"]
                elif i.has_attr("src"):
                    res["type"] = i.name
                    res["resource"] = i["src"]

                if res not in resources and res != {}:
                    if res["resource"][0] != '/' and res["resource"][0] != '#' and not re.search(cfc_url, res["resource"]):
                        resources.append(res)

        return resources

    def hrefs(self):
        """
            Cycles through all <a> tags on the page and returns a list
            of all the hrefs found in order.
        """
        hrefs = []

        if not self.soup or not self.page:
            return hrefs

        for a in self.soup.find_all("a", href=True):
            if a["href"] not in hrefs:
                hrefs.append(a["href"])

        return hrefs

    def privacy(self):
        """
            Uses the hrefs() function to get all <a> tags and then checks
            for the phrase 'privacy-policy' in each href and returns the
            one that matches. Otherwise we will just return None.
        """
        hr = self.hrefs()
        for href in hr:
            if "privacy-policy" in href:
                return href
        return None

    def wordcount(self):
        """
            Cycles through every visible word on the page and returns a
            dict holding words and their number of occurrences on the page.
        """
        freq = {}

        if not self.soup or not self.page:
            return freq

        words = [word.lower() for word in self.soup.get_text().split()]
        for word in words:
            if word in freq.keys():
                freq[word] = freq[word] + 1
            else:
                freq[word] = 1
        return freq

if __name__ == "__main__":
    cfc_url = "https://www.cfcunderwriting.com"

    # Create initial scraper
    scraper = Scraper()
    scraper.open(cfc_url)
    external = scraper.external_links()
    hrefs = scraper.hrefs()
    policy_url = scraper.privacy()

    # Print all hyperlinks in order and identify privacy policy url
    print("\nList of all hyperlinks (anchor tags) on the page:\n")
    for i in range(0, len(hrefs)):
        print(str(i) + ": " + hrefs[i])
    print("\nPrivacy policy URL was found at: " + policy_url  + "\n")

    if not os.path.exists("output"):
        os.makedirs("output")

    # Create JSON file with all externally loaded resources (types included)
    print("Creating JSON file for all external resources hosted on " + cfc_url)
    external_file = open("output/external_links.json", "w")
    external_file.write(json.dumps(external, indent=4, sort_keys=False))
    external_file.close()

    # Create a JSON file with all word occurrences of the privacy policy page
    # If the privacy policy page is not available, we'll skip this
    if policy_url != None:
        print("Creating JSON file for all word occurrences at " + cfc_url + policy_url)
        privacyScraper = Scraper()
        privacyScraper.open(cfc_url + policy_url)
        occs = privacyScraper.wordcount()
        occs_file = open("output/word_count.json", "w")
        occs_file.write(json.dumps(occs, indent=4, sort_keys=True))
        occs_file.close()
    else:
        print("JSON file for word occurrences was skipped as privacy policy page was not found.")

    print("Done!")