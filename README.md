# Extracting the citations from the (English) Wikipedia to check if they are hallucinated

I have had the idea to check how many citations have contained fake content for some time, after reading some news
articles about the prevalence of AI-hallucinated content on Wikipedia.
I used the dump conducted on 2026/01/01 to extract the citations.

Now that I have downloaded the dumps for the English Wikipedia from 2026/04/01, maybe I will do the analysis on the
newer citations in English Wikipedia.

The dataset is provided in two parts.
- sorted.parquet, where each row is composed of one citation block and the title of the associated Wikipedia article.
- tags.parquet, where the `tags = rest` sections of the citations are grouped together by `tags`.

## Wrangling the _Dump_

The recent dumps are around 25GB compressed, which does not seem much, but it exceeds 100GB when decompressed, so
special measures will have to be taken if you do not have a few hundred GBs of RAM lying around. wink
wink

I first decompressed the zipped file and parsed the XML tree using the python package xml.etree.ElementTree .

Then, I extracted the title, ID and Wikitext from every `<page>`-tagged node.

To document the format, there is one `site-info` node and many `page` nodes under the root node. The `page` nodes each
contain a namespace value, and 0 means that it is a proper article. Each article also carries a unique ID but the titles
may not be unique due to the process used to generate the archive.

## What counts as a citation?

After formatting the data to fit inside a Polars DataFrame, I proceeded with the extraction of citations. There was much
agony in regexes, but I survived.

### Technical detour: Why not Pickle?

I tried using pickle to read and write initially and both its slowness and largeness was off-putting. I remembered that
Gemini told me that I could try to use Polars and decide to give it a go.
It turns out that storing the data in Parquet was a huge space-saver and storing an IPC allowed near-instant loading of
the data. In terms of the opposite characteristics, Parquet wasn't too slow (faster than pickle) and IPC wasn't too
big (smaller than pickle) either.
Also, it allowed me to do the data manipulations much faster than any pure Python data structure can offer.

## Pre-historic citation dataset

I found out that there was a team in 2020 who did
the [same thing (with different methods)](https://arxiv.org/abs/2007.07022), which should provide a good baseline for
the pre-LLM
era.

## Analysis of the _Dump_

The preliminary citations have been stored as Parquet files and can be found
on [Hugging Face](https://huggingface.co/datasets/chosummingcuhk/wikipedia-citations-enwiki-20260101).
Initially, there were lots of junk. Thankfully, after some aggressive _regexing_, I managed to make the data look more
presentable.

### arXiv citations

I tried to resolve all (easily-)extracted arXiv ids and none of them are hallucinated. However, further analysis awaits
for whether the titles given in the citations match with the resolved arxiv id.

### DOI and ISBN

It turns out that there are many hurdles to extracting these identifiers programmatically while considering the various
formats and contexts that they can show up in.

## Epilogue: Jumbo citations

As an honourable mention, there are 8 jumbo citations stemming from giant collaboration papers in biology and physics.
They had to be dealt with separately because the citations are **over 10,000 characters** long.
They were cited **unabridged** in the Wikitext. The (real and non-hallucinated) papers and the associated articles are
shown below.

| Papers                                                                                                                                                                                                                                                                      | Articles                                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Global, regional, and national incidence, prevalence, and years lived with disability for 310 diseases and injuries, 1990–2015: a systematic analysis for the Global Burden of Disease Study 2015". The Lancet. 388 (10053): 1545–1602. doi:10.1016/S0140-6736(16)31678-6. | Cysticercosis                                                                                                                                                                                                                                                                                                                                                                                            |
| "Technical design report for the PANDA (AntiProton Annihilations at Darmstadt) Straw Tube Tracker: Strong interaction studies with antiprotons". The European Physical Journal A. 49 (2): 23–38. arXiv:1205.5441. doi:10.1140/epja/i2013-13025-8.                           | Straw chamber                                                                                                                                                                                                                                                                                                                                                                                            |
| "The Seventeenth Data Release of the Sloan Digital Sky Surveys: Complete Release of MaNGA, MaStar, and APOGEE-2 Data". The Astrophysical Journal Supplement Series. 259 (2): 35. arXiv:2112.02026. Bibcode:2022ApJS..259...35A. doi:10.3847/1538-4365/ac4414.               | HD 271182                                                                                                                                                                                                                                                                                                                                                                                                |
| "Dynamic incorporation of multiple in silico functional annotations empowers rare variant association analysis of large whole-genome sequencing studies at scale". Nature Genetics. 52 (9): 969–983. doi:10.1038/s41588-020-0676-4.                                         | Bioinformatics                                                                                                                                                                                                                                                                                                                                                                                           |
| "Odderon Exchange from Elastic Scattering Differences between pp and ppbar Data at 1.96 TeV and from pp Forward Scattering Measurements". Physical Review Letters. 127 (6) 062003. arXiv:2012.03981. doi:10.1103/PhysRevLett.127.062003.                                    | TOTEM experiment                                                                                                                                                                                                                                                                                                                                                                                         |
| "Increasing the Astrophysical Reach of the Advanced Virgo Detector via the Application of Squeezed Vacuum States of Light". Physical Review Letters. 123 (23) 231108. Bibcode:2019PhRvL.123w1108A. doi:10.1103/PhysRevLett.123.231108.                                      | Carlton M. Caves                                                                                                                                                                                                                                                                                                                                                                                         |
| "The 2024 Outline of Fungi and fungus-like taxa". Mycosphere. 15 (1): 5146–6239. doi:10.5943/mycosphere/15/1/25.  (Some of them even point to the **specific page(s)** on which the genera/species/family/order appeared.)                                                  | _Gomphillaceae_, _Xylariales_, _Kudratovia_, _Bryogomphus_, _Lueckingia_, _Buelliastrum_, _Caliciopsis_, _Tayloriellina_, _Buelliella_, _Himantormia_, _Waynea_, _Phyllocraterina_, _Trypetheliopsis boninensis_, _Hosseusia_ (fungus), _Parainoa_, _Sipmanidea_, _Aptrootidea_, _Verruciplaca_, _Bezerroplaca_, _Batistomyces_, _Roselviria_, _Vezdamyces_, _Caleniella_, _Adelphomyces_, _Aulaxinella_ |
