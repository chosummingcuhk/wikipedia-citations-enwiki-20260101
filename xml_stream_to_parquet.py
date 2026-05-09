import xml.etree.ElementTree as ET
import polars as pl

ns_map = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
ns_prefix = '{http://www.mediawiki.org/xml/export-0.11/}'

stems = ['enwiki-2026-05-01-p80590276p83077138','enwiki-2026-05-01-p76112843p80590275','enwiki-2026-05-01-p71618412p76112841']

# input assumed decompressed
for stem in stems:
    context = ET.iterparse(f'{stem}.xml', events=('end', 'start'))
    _, root_node = next(context)  # first 'start' event = root element

    print("Beginning filtration of ElementTree...")
    t = []
    w = []
    i = []

    batch_size = 100_000
    counter = 0

    for event, elem in context:
        if event != "end":
            continue
        #capture entire page
        if elem.tag == f"{ns_prefix}page":
            skip = False
            title = None
            ident = None
            wikitext = None
            # load various elements
            for child in elem:
                if child.tag == f"{ns_prefix}title":
                    title = child.text
                if child.tag == f"{ns_prefix}id":
                    ident = child.text
                if child.tag == f"{ns_prefix}redirect":
                    skip = True
                    break
                if child.tag == f"{ns_prefix}ns" and (child.text != '0' and child.text is not None):
                    skip = True
                    break
                if child.tag == f"{ns_prefix}revision":
                    for childchild in child:
                        if childchild.tag == f"{ns_prefix}text":
                            wikitext = childchild.text
            if skip:
                continue
            t.append(title)
            w.append(wikitext)
            i.append(int(ident))
            # Progress indicator every 10K articles
            if len(t) % 10000 == 0:
                print(f"Captured {counter * 10 + len(t) // 10000}0K articles...")
            if len(t) >= batch_size:
                df = pl.DataFrame({'id': i, 'title': t, 'wikitext': w})
                df.write_ipc(f'{stem}_{counter}.ipc')
                t = []
                w = []
                i = []
                counter += 1
            root_node.clear()

    print(f"Filtration complete.")

    if i:
        df = pl.DataFrame({'id': i, 'title': t, 'wikitext': w})
        df.write_ipc(f'{stem}_{counter}.ipc')
    l = []
    for x in range(counter+1):
        l.append(pl.read_ipc(f'{stem}_{x}.ipc'))
    df = pl.DataFrame()
    for x in l:
        df = df.vstack(x)
    df.rechunk()
    df.write_parquet(f'{stem}.parquet')
