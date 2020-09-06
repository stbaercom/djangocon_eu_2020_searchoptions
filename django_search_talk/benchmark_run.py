import requests
import time
import pandas
import logging


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

def main(fn,ofn):
    result = {}
    modes = ['SQL Contains', "SQL Search", "Simple FTS", "Ranked FTS with Cutoff",
             "Indexed Simple FTS", "Indexed Ranked FTS with Cutoff", "Faceted Elastic Search"]
    for i in range(5):
        for word in open(fn, mode='r', encoding='utf-8'):
            word = word.strip()
            for mode in modes:
                start = time.time()
                try:
                    ok, _ = query(mode,word)
                except:
                    ok = False
                end = time.time()
                diff = (end - start) * 1000.0
                for n,v in [("mode",mode), ("word",word),("time",diff),("ok",ok),("run",i)]:
                    result.setdefault(n,[]).append(v)
                logging.info(f"{mode}, {word}, {diff} {ok} {i}")

    df = pandas.DataFrame.from_dict(result)
    df.to_excel(ofn)







def query(qtype, qstring):
    tmp = f"http://localhost:8000/reviews/search"
    r = requests.get(tmp, {"qtype": qtype, "qstring": qstring, 'qnum':3})
    return r.ok, r.text


if __name__ == '__main__':
    main("words.txt", "bench.xlsx")
