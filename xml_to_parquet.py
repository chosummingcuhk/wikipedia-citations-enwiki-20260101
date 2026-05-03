# This script assumes that you can hold the WHOLE XML FILE in RAM.
import xml.etree.ElementTree as ET
import polars as pl
ns_map = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
ns_prefix = '{http://www.mediawiki.org/xml/export-0.11/}'


root_node = ET.parse('enwiki-20260401-pages-articles.xml').getroot()
print("Beginning filtration of ElementTree...")
t =[]
w=[]
i=[]
# 2. Iterate directly over the root children
# This avoids .findall() which creates a secondary list of objects
for child in root_node:

    # Check if the branch is a 'page'
    if child.tag != f"{ns_prefix}page":
        continue

    # Filter A: Only Namespace 0 (Articles)
    ns_elem = child.find('mw:ns', ns_map)
    if ns_elem is None or ns_elem.text != '0':
        continue

    # Filter B: Discard Redirects (No content/citations)
    if child.find('mw:redirect', ns_map) is not None:
        continue

    # 3. Extract Core Data Components
    title_elem = child.find('mw:title', ns_map)
    id_elem = child.find('mw:id', ns_map)
    text_elem = child.find('mw:revision/mw:text', ns_map)

    title = title_elem.text if title_elem is not None else None
    id = id_elem.text if id_elem is not None else None
    wikitext = text_elem.text if text_elem is not None else None

    t.append(title)
    w.append(wikitext)
    i.append(int(id))

    # Progress indicator every 1M articles
    if len(t) % 1000000 == 0:
        print(f"Captured {len(t) // 1000000}M articles...")
        print(child.find('mw:title', ns_map).text)

print(f"Filtration complete.")

df = pl.DataFrame({'id':i, 'title':t,'wikitext':w})
df.write_parquet('enwiki-20260401-pages-articles.parquet')
