import typer
import re
import os
import glob
import json
import shutil
import unidic2ud

app = typer.Typer()

"""
2023-12-03 01:54:15 INFO Epoch 1 / 1000:
2023-12-03 01:55:07 INFO dev:   - loss: 2.1349 - UCM: 17.67% LCM:  7.14% UAS: 63.58% LAS: 49.57%
2023-12-03 01:55:15 INFO test:  - loss: 2.3775 - UCM: 17.92% LCM:  7.74% UAS: 62.13% LAS: 48.08%
"""

@app.command()
def scores(logfile: str):
    epoch_ptn = re.compile(r".+INFO Epoch (\d+) / (\d+):")
    dev_ptn = re.compile(r".+INFO dev:.+ loss: ([\d\.]+) - UCM:\s+([\d\.]+).+LCM:\s+([\d\.]+).+ UAS:\s+([\d\.]+).+ LAS:\s([\d\.]+)\%")
    test_ptn = re.compile(r".+INFO test:.+ loss: ([\d\.]+) - UCM:\s+([\d\.]+).+LCM:\s+([\d\.]+).+ UAS:\s+([\d\.]+).+ LAS:\s([\d\.]+)\%")

    with open(logfile) as f:
        data = list()
        r = None
        ptn = epoch_ptn
        for line in f:
            m = ptn.match(line)
            if m is not None:
                if ptn == epoch_ptn:
                    r = dict()
                    r["epoch"] = int(m.group(1))
                    r["num_epochs"] = int(m.group(2))
                    ptn = dev_ptn
                elif ptn == dev_ptn:
                    r["dev_loss"] = float(m.group(1))
                    r["dev_UCM"] = float(m.group(2))
                    r["dev_LCM"] = float(m.group(3))
                    r["dev_UAS"] = float(m.group(4))
                    r["dev_LAS"] = float(m.group(5))
                    ptn = test_ptn
                elif ptn == test_ptn:
                    r["test_loss"] = float(m.group(1))
                    r["test_UCM"] = float(m.group(2))
                    r["test_LCM"] = float(m.group(3))
                    r["test_UAS"] = float(m.group(4))
                    r["test_LAS"] = float(m.group(5))
                    data.append(r)
                    ptn = epoch_ptn
    print(json.dumps(data, indent=True))


@app.command()
def dcp(basedir: str, source: str, target: str):
    basepath = os.path.abspath(basedir)
    if not os.path.exists(target):
        os.makedirs(target)
    for fname in glob.glob(os.path.join(basedir, source)):
        fpath = os.path.abspath(fname)
        relpath = fpath.removeprefix(basepath)
        if relpath.startswith("/"):
            relpath = relpath[1:]
        tpath = os.path.join(target, relpath)
        tdir = os.path.dirname(tpath)
        if not os.path.exists(tdir):
            os.makedirs(tdir)
        print(fpath, relpath, target, tpath)
        shutil.copyfile(fpath, tpath)

def to_str(v):
    if v is None:
        return "_"
    return str(v)

@app.command()
def parseja(text: str, model: str="ja_gsd.mbert", dic: str="kindai"):
    from diaparser.parsers import Parser
    parser = Parser.load(model)
    nlp = unidic2ud.load(dic)
    sentence = nlp(text)
    tokens = [t.form for t in sentence]
    dataset = parser.predict([tokens[1:]], prob=True)

    print(f"# text = {text}")
    for t, u in zip(sentence[1:], dataset.sentences[0].to_tokens()):
        line = [t.id, t.form, t.lemma, t.upos, t.xpos, t.feats, u["head"], u["deprel"], t.deps, t.misc]
        line = [to_str(s) for s in line]
        print("\t".join(line))
    print()

@app.command()
def parseconllu(conllufile: str, model: str="ja_gsd.mbert", dic: str="kindai"):
    from conllu import parse_incr
    from diaparser.parsers import Parser
    parser = Parser.load(model)

    with open(conllufile) as f:
        for tokenlist in parse_incr(f):
            tokens = [t["form"] for t in tokenlist]
            dataset = parser.predict([tokens], prob=True)
            print(f"# text = {tokenlist.metadata['text']}")
            for t, u in zip(tokenlist, dataset.sentences[0].to_tokens()):
                line = [t["id"], t["form"], t["lemma"], t["upos"], t["xpos"], t["feats"], u["head"], u["deprel"], t["deps"], ",".join([f"{k}={v}" for k, v in t["misc"].items()])]
                line = [to_str(s) for s in line]
                print("\t".join(line))
            print()


if __name__ == "__main__":
    app()