import typer
import json
import re
from bs4 import BeautifulSoup

app = typer.Typer()

@app.command()
def tojsonl(fname: str):
    with open(fname) as f:
        xml = f.read()
    soup = BeautifulSoup(xml, 'html.parser')
    for e in soup.find_all("note"):
        e.decompose()
    for e in soup.find_all("ruby"):
        e.decompose()

    for div in soup.find_all("div"):
        id_ = div.get("id")
        if id_ is None:
            continue
        r = dict()
        for div2 in div.findChildren("div"):
            t = div2.get("type")
            if t == "古典本文":
                r["original"] = div2.text.strip().replace("\n", "")
            elif t == "現代語訳":
                r["translated"] = div2.text.strip().replace("\n", "")
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    app()