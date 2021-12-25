# %%
from re import search
from notion.block import CollectionViewBlock
from notion.client import NotionClient
from datetime import datetime
from notion.utils import slugify
import time
import pytz
# NOTION_TOKEN = "52d96b318c7cda25f7a98b44993aa8b8324da48affaa4a7e1f03775e65164acd59bb137a29b972185795fa4aec337425b442f96b1eb017a7459e56b5552dc24e374530b1ef90909c1d62d34124a2"
client = NotionClient(email="haofan.17@intl.zju.edu.cn", password="asd70asd")
# %% Get the date
timezone = pytz.timezone("US/Pacific")
dt = datetime.now(timezone)
date = dt.strftime('%Y-%m-%d')
day = dt.strftime('%A')
# print(date, day)
# %% Define Collection Schema
def get_collection_schema():
    return {
        "ckbx": {"name": "Checked", "type": "checkbox"},
        "title": {"name": "Name", "type": "title"},
    }

def iSlugify(name):
    tmp = name.split('_')
    res = ''
    for w in tmp:
        res += w.capitalize()
    return res

def traverseDocTree(url_or_id, depth = 0):
    parent = client.get_block(url_or_id)
    try:
        print('\t'*depth+"|--"+parent.title)
    except:
        print('\t'*depth+"|--"+parent.id)
    if len(parent.children) > 0:
        for child in parent.children:
            traverseDocTree(child.id, depth+1)

def syncParentFromChild(record,difference, **kwargs):
    """
    If the to-do entry in child's table is checked/unchecked,
    sync the change to the parent block
    """
    parent_row = kwargs["target"]
    item = slugify(record.title)
    for diff in difference:
        action = diff[0]
        if action == 'add':
            parent_row.set_property(item, True)
            print('[Child] Add item', item)
        elif action == 'change':
            change = diff[2]
            if change[0] == 'Yes' and change[1] == 'No':
                parent_row.set_property(item, False)
            else:
                parent_row.set_property(item, True)
            print("[Child] Change item ", item, "from", change[0], "to", change[1])
    # if record.checked:
    #     parent_row.set_property(prop_to_sync, True)
    # else:
    #     parent_row.set_property(prop_to_sync, False)
    # parent_row.refresh()

def syncChildFromParent(difference,**kwargs):
    """
    If the to-do entry in the parent's table is checked/unchecked,
    sync the change to the parent block
    """
    child_cvb = kwargs["target"]
    for diff in difference:
        action = diff[0]
        try:
            if action == 'add':
                prop_id = diff[2][0][0]
                prop_name = id_to_name[prop_id]
                if prop_name in habits:
                    prop_row = child_cvb.collection.get_rows(search = prop_name)[0]
                    prop_row.checked = True
                print('[Parent] Add', prop_name)
            elif action == 'change':
                prop_id = diff[1][1]
                prop_name = id_to_name[prop_id]
                if prop_name in habits:
                    prop_row = child_cvb.collection.get_rows(search = prop_name)[0]
                    change = diff[2]
                    if change[0] == 'Yes' and change[1] == 'No':
                        prop_row.checked = False
                    elif change[0] == 'No' and change[1] == 'Yes':
                        prop_row.checked = True
                    print("[Parent]Change property", id_to_name[prop_id], "from", change[0], "to", change[1])
        except:
            pass
#%% 
main_db_url = "https://www.notion.so/explever/6df1bf9a913c4564805113fc0a2ba40e?v=a776eccfaffc48c9a6b716ca1e7af137"
main_cvb = client.get_collection_view(main_db_url)
daily_row = main_cvb.collection.add_row()
daily_row.Date = date
daily_row.Day = day
schema_props = main_cvb.collection.get_schema_properties()
id_to_name = {}
habits = []
for item in schema_props:
    id_to_name[item['id']] = item['name']
    if item['name'] not in ['Completeness', 'Created Date', 'Date','Day']:
        habits.append(item['name'])

#%% Link to the homepage child database
homepage_db_url = 'https://www.notion.so/explever/216078c7c899471b9bda21e2c6f7f22d?v=7a0b317e28624bba85fb7974406b4242'
homepage_cvb = client.get_collection_view(homepage_db_url).parent
# print(type(homepage_cvb))
homepage_cvb.title = date
homepage_db_rows = homepage_cvb.collection.get_rows()
n_row_to_add = len(habits) - len(homepage_db_rows)
for i in range(n_row_to_add):
    homepage_cvb.collection.add_row()

homepage_db_rows = homepage_cvb.collection.get_rows()
for i in range(len(habits)):
    row = homepage_db_rows[i]
    row.title = habits[i]
    row.checked = False
    row.add_callback(syncParentFromChild, None,{"target": daily_row, "item": slugify(row.title)})
daily_row.add_callback(syncChildFromParent, None, {"target": homepage_cvb})

#%% Calculate the completeness
daily_items = daily_row.get_all_properties()
n_items = len(daily_items.keys())-4
n_completed = 0
for v in daily_items.values():
    if v == True:
        n_completed += 1
daily_row.set_property('completeness', n_completed/n_items)
#%% Refresh the pages
cur_date = date
while(date == cur_date):
    cur_dt = datetime.now()
    cur_date = cur_dt.strftime('%Y-%m-%d')
    daily_row.refresh()
    for row in homepage_db_rows:
        row.refresh()
    n_completed = 0
    daily_items = daily_row.get_all_properties()
    n_items = len(daily_items.keys())-4
    for v in daily_items.values():
        if v == True:
            n_completed += 1
    completeness = n_completed/n_items
    if completeness > 1:
        completeness = 1
    daily_row.set_property('completeness', completeness)
    
    time.sleep(5)
