from re import search
from notion.block import CollectionViewBlock
from notion.client import NotionClient
from datetime import datetime
from notion.utils import slugify
import time
import pytz
import os

class Ohara:
    def __init__(self, rootDir):
        NOTION_TOKEN = "d4d10d275f8276e12feb0514ad859549f8adc335f69db3ddac629fc3c2ad80fdd192a82d299717756bcfe5658fd38d57459bcb53edb586d8c7d9a5e33f6c50544e998c3f5a177c94173065954f3d"
        self.client = NotionClient(token_v2=NOTION_TOKEN)
        self.parent_url = "https://www.notion.so/explever/b999c9e3f31d4d7ea14e223615146901?v=0ff45635a2e744c494e57c118a115f88"
        self.parent_page = self.client.get_collection_view(self.parent_url)
        self.rootDir = rootDir

    def add_entry_from_file(self, fname):
        entry_row = self.parent_page.collection.add_row()
        entry_row.set_property(slugify("Status"), "unread")
        with open(fname, 'r', encoding='utf-8') as f:
            raw = f.readlines()
            for i in range(len(raw)):
                line = raw[i].strip().lstrip("\t")
                if line.startswith("author"):
                    author_list = line[line.find("{")+1:line.rfind("}")].split('and')
                    author_list_item = []
                    for author in author_list:
                        if author.find(",") >= 0:
                            comma = author.find(",")
                            first = author[comma+2:].strip()
                            last = author[:comma].strip()
                            author_list_item.append(first+" "+last)
                        else:
                            author_list_item.append(author.strip())
                    # print(author_list_item)
                    entry_row.set_property(slugify("Authors"), author_list_item)
                elif line.startswith("title"):
                    title = line[line.find("{")+1:line.rfind("}")]
                    entry_row.set_property(slugify("Title"), title)
                elif line.startswith("year"):
                    year = line[line.find("{")+1:line.rfind("}")]
                    entry_row.set_property(slugify("Year"), year)
                elif line.startswith("url"):
                    url = line[line.find("{")+1:line.rfind("}")]
                    entry_row.set_property(slugify("URL"), url)
                elif line.startswith("keywords"):
                    keywords_list = line[line.find("{")+1:line.rfind("}")]
                    entry_row.set_property(slugify("Keywords"), keywords_list)
                elif line.startswith("series"):
                    series = line[line.find("{")+1:line.rfind("}")]
                    entry_row.set_property(slugify("Series"), series)
                elif line.find("NSDI") >= 0:
                    start = line.find("NSDI")
                    series = line[start:start+7]
                    tmp = series.split(" ")
                    entry_row.set_property(slugify("Series"), " \'".join(tmp))

    def add_files_from_dir(self):
        for dirName, subdirList, fileList in os.walk(self.rootDir):
        # print('Found directory: %s' % dirName)
            for fname in fileList:
                fpath = dirName+"/"+fname
                self.add_entry_from_file(fpath)
    
    def get_notion_page_url(self):
        return self.parent_url

if __name__ == '__main__':
    ohara = Ohara('../bib')
    ohara.add_files_from_dir()
    print("Done!")