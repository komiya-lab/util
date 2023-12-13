import typer
import sys
import json
import glob
import os
import spacy
import csv
import unidic2ud
from bs4 import BeautifulSoup

app = typer.Typer()

@app.command()
def tojsonl(fname: str):
    with open(fname) as f:
        xml = f.read()
    soup = BeautifulSoup(xml, 'html.parser')
    nlp = spacy.load("ja_core_news_sm")
    for e in soup.find_all("note"):
        e.decompose()
    for e in soup.find_all("rt"):
        e.decompose()

    for div in soup.find_all("div"):
        id_ = div.get("id")
        if id_ is None:
            continue
        org = None
        trn = None
        for div2 in div.findChildren("div"):
            t = div2.get("type")
            if t == "古典本文":
                org = div2.text.strip().replace("\n", "")
            elif t == "現代語訳":
                trn = div2.text.strip().replace("\n", "")
        
        if org is None or trn is None:
            continue
        orgs = list(nlp(org).sents)
        trns = list(nlp(trn).sents)
        if len(orgs) != len(trns):
            continue
        for o, t in zip(orgs, trns):
            if len(o) == 0 or len(t) == 0:
                continue
            r = {
                "original": o.text,
                "translated": t.text
            }
            print(json.dumps(r, ensure_ascii=False))


def ud2dic(t):
    try:
        return {"id": t.id, "form": t.form, "lemma": t.lemma,
                "upos": t.upos, "xpos": t.xpos, "feats": t.feats, "head": t.head.id,
                "deprel": t.deprel, "deps": t.deps, "misc": t.misc}
    except AttributeError:
        return {"id": t.id, "form": t.form, "lemma": t.lemma,
                "upos": t.upos, "xpos": t.xpos, "feats": t.feats, "head": -1,
                "deprel": t.deprel, "deps": t.deps, "misc": t.misc}


@app.command()
def udparse(fname: str, dic: str, outsuffix: str= None, target: str="original"):
    nlp=unidic2ud.load(dic)
    if outsuffix is None:
        out = sys.stdout
    else:
        print(fname)
        out = open(f"{fname}.{target}_{dic}.jsonl", "w")
        
    with open(fname) as f:
        for line in f:
            js = json.loads(line)
            s = nlp(js[target])
            try:
                js[f"{target}_conllu"] = str(s)
            except AttributeError:
                print(line.strip(), file=out)
                continue
            js[f"{target}_tokens"] = [ud2dic(t) for t in s]
            js[f"{target}_dic"] = dic
            print(json.dumps(js, ensure_ascii=False), file=out)

    if outsuffix is not None:
        out.close()


@app.command()
def conllu(fname: str, dic: str, parser, target: str="original"):
    nlp = unidic2ud.load(dic, parser)
    out = open(f"{fname}.{target}_{dic}_{parser}.conllu", "w")

        
    with open(fname) as f:
        for line in f:
            js = json.loads(line)
            s = nlp(js[target])
            try:
                conllu = str(s)
                print(conllu, file=out)
            except:
                print(line, file=sys.stderr)

    out.close()


@app.command()
def unidictype(basedir: str):
    res = dict()
    for fname in glob.glob(os.path.join(basedir, "*.rpt")):
        print(fname, file=sys.stderr)
        basename = os.path.basename(fname)
        dicname = basename.replace(".rpt", "").replace("corpus_", "")
        if dicname in ["csj", "qkana"]:
            continue
        with open(fname) as f:
            reader = csv.reader(f, delimiter="\t")
            corpora = list()
            for row in reader:
                if len(row) < 2:
                    continue
                corpus = row[1]
                if "file:" in corpus:
                    corpus = corpus.replace("file:", "")
                if corpus not in corpora:
                    corpora.append(corpus)
            res[dicname] =corpora
    print(json.dumps(res, indent=True, ensure_ascii=False))


if __name__ == "__main__":
    app()