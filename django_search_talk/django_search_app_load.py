import logging
import os
import datetime
import hashlib

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_search_talk.settings')

import django

django.setup()

from django_search_app.models import FTSReview



from django_search_app.elastic_helper import write_elastic

BATCHSIZE = 100

def map_text(name):
    def func(val):
        return {name: val}
    return func


def map_help(val):
    help, full = val.strip().split("/")
    return {"review_help_total": int(full),
            "review_help_help": int(help)}


def map_score(val):
    return {"review_score": float(val.strip())}


def map_time(val):
    tz = datetime.timezone.utc
    ds = int(val.strip())
    return {"review_time": datetime.datetime.fromtimestamp(ds,tz=tz)}


MAPPING = {
    "product/productId": map_text("productId"),
    "review/userId": map_text("userId"),
    "review/profileName": map_text("name"),
    "review/helpfulness": map_help,
    "review/score": map_score,
    "review/time": map_time,
    "review/summary": map_text("review_summary"),
    "review/text": map_text("review_text")
}



def writedb(vals):

    acum = {}

    logging.info("Starting DB Update")
    FTSReview.objects.all().delete()

    logging.info("DB Cleanup Done")
    for i, val in enumerate(vals):
        if i % BATCHSIZE == 0:
            logging.info(f"Written {i} datasets")

        entry = FTSReview(**val)
        entry.save()
        entry_id = entry.id
        acum[entry_id] = val

    return acum
    logging.info("Done with DB Update")


def readfile(filename):
    logging.info("Loading Input File")
    names = {}
    acum = []
    for entry in read_entry(filename):
        acum.append(entry)
    return acum


def read_entry(filename):
    i = 0
    entry = {}
    for line in open(filename, mode="r", encoding="utf-8", errors="replace"):
        line = line.strip()
        if line == "":
            i += 1
            if i % BATCHSIZE == 0:
                logging.info(f"Record {i} read")

            yield entry
            entry = {}
            continue
        field, content = line.split(":", 1)
        fn = MAPPING[field]
        val = fn(content.strip())
        entry.update(val)
    yield entry


def rewrite_name(entry):
    name = entry['name']
    m = hashlib.sha256()
    m.update(name)
    entry['name'] = m.hexdigest()


def main(filename):
    vals = readfile(filename)
    vals_with_id = writedb(vals)
    write_elastic("reviews",vals_with_id)


if __name__ == '__main__':
    main("movies_1m.txt")
