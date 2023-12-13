import typer
import re
import os
import glob
import json
import shutil

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


if __name__ == "__main__":
    app()