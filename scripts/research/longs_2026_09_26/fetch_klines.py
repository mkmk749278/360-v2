"""1m klines from the public Binance archive (data.binance.vision) for the
close day and the day after of every LONG closed in the last 62 days.

Writes a URL list and downloads it with parallel curl. Resumable."""
import datetime as dt
import os
import subprocess
import urllib.parse

from common import DATA, END, load_rows

rows = load_rows()
need = set()
for r in rows:
    if r["direction"] != "LONG" or r["t"] < END - dt.timedelta(days=62):
        continue
    for k in (0, 1):
        d = (r["t"] + dt.timedelta(days=k)).date()
        if d <= dt.date(2026, 9, 25):  # the archive trails by a day
            need.add((r["symbol"], d.isoformat()))
kl = os.path.join(DATA, "kl")
os.makedirs(kl, exist_ok=True)
lst = os.path.join(DATA, "urls.txt")
with open(lst, "w") as f:
    for s, d in sorted(need):
        q = urllib.parse.quote(s)
        f.write(f"https://data.binance.vision/data/futures/um/daily/klines/"
                f"{q}/1m/{q}-1m-{d}.zip {kl}/{s}__{d}.zip\n")
print(len(need), "symbol-days")
subprocess.run(
    f"cat {lst} | xargs -P 12 -n 2 sh -c "
    "'[ -s \"$1\" ] || curl -sS -m 60 -f -o \"$1\" \"$0\" 2>/dev/null; true'",
    shell=True, check=False)
print(len(os.listdir(kl)), "files")
