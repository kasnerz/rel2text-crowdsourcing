import os
import requests
import json
import lxml.html
import numpy as np
import pandas as pd
import socket
import glob
import logging
from pprint import pprint as pp
from datetime import datetime
from flask import Flask, render_template, jsonify, request, url_for
from collections import defaultdict
from datetime import datetime

from collections import namedtuple

np.random.seed(42)

Args = namedtuple("Args", "in_file num_rel out_dir compl_code")
app = Flask(__name__)

app.config["prefix"] = "./app/"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    # filename="log/run.log", filemode='a')
logger = logging.getLogger(__name__)

# fh = logging.FileHandler('log/run.log', mode="a")
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)


def get_existing_indices():
    existing_indices = set()
    # existing_ids_path = f"{args.out_dir}/ids.txt"

    # if not os.path.exists(existing_ids_path):
    #     with open(existing_ids_path, "w"):
    #         # create file and exit
    #         pass
    #     return existing_indices
    # else:
    #     with open(existing_ids_path, "w"):


    for path in glob.glob(app.args.out_dir + '/*.tsv'):
        df = pd.read_csv(path, sep='\t', header=None, usecols=[0])
        indices = df.iloc[:, 0].to_numpy().tolist()
        existing_indices.update(indices)

    return existing_indices

def prepare_data(data, num_rel):
    try:    
        existing_indices = get_existing_indices()
    except:
        existing_indices = []

    if existing_indices and len(existing_indices) + num_rel < data.shape[0]:
        # filter out relations for which we have descriptions
        data = data[~data["id"].isin(existing_indices)]  

    logger.info("Sampling relations from " + str(data.shape[0]) + " rows")
    rels = data.sample(num_rel)
    data_run = []

    # i = 0

    # while i < num_rel:
    #     idx = app.perm[app.idx % app.nr_rows] 
    #     rel = data.iloc[idx]

    for _, rel in rels.iterrows():
        d = {
            "ex_id" : str(rel["id"]),
            "rel_uri" : str(rel["rel_uri"]),
            "subj_name" : str(rel["subject"]),
            "obj_name" : str(rel["object"]),
            "rel_name" : str(rel["relation"]),
        }
        for desc in ["rel_desc", "subj_desc", "obj_desc"]:
            if rel[desc] is not np.nan:
                d[desc] = rel[desc]

        # app.idx += 1
        # i += 1
        data_run.append(d)

    logger.info("Selected examples: " + str([int(e["ex_id"]) for e in data_run]))
    return data_run

def load_data(args):
    app.data = pd.read_csv(args.in_file)
    app.nr_rows = app.data.shape[0]

    logger.info(f"Loaded {app.nr_rows} rows")

    # app.perm = np.random.permutation(range(app.nr_rows))
    # app.idx = 0

    # logger.info(f"Permutation of indices: " + str(app.perm))


@app.route('/', methods=['GET', 'POST'])
def index():
    prolific_pid = request.args.get('PROLIFIC_PID')
    study_id = request.args.get('STUDY_ID')
    session_id = request.args.get('SESSION_ID')

    logger.info(f"Page loaded")
    logger.info(f"PROLIFIC_PID: {prolific_pid}")
    logger.info(f"STUDY_ID: {study_id}")
    logger.info(f"SESSION_ID: {session_id}")

    data_run = prepare_data(data=app.data, num_rel=app.args.num_rel)

    return render_template('index.html', data=data_run, num_rel=app.args.num_rel, \
        prefix=app.config["prefix"], prolific_pid=prolific_pid, session_id=session_id, study_id=study_id,
        compl_code=app.args.compl_code)


@app.route('/submit', methods=['POST'])
def submit():
    j = request.get_json()
    responses = j["out"]
    logger.info("Responses")
    logger.info(str(responses))
    os.makedirs(app.args.out_dir, exist_ok=True)

    if "prolific_pid" in j and j["prolific_pid"] != "None":
        prolific_pid = j["prolific_pid"]
        study_id = j["study_id"]
        session_id = j["session_id"]
        out_filename = f"{app.args.out_dir}/{study_id}_{prolific_pid}.tsv"
    else:

        timestamp = int(datetime.now().timestamp())
        out_filename = f"{app.args.out_dir}/test_{timestamp}.tsv"

    logger.info(f"Saving responses to file {out_filename}")
    df = pd.DataFrame(responses)

    columns = ["example_id", "response", "relation", "subject", "object", "flags"]
    df = df.reindex(columns, axis=1)
    df.to_csv(out_filename, sep="\t", index=None, header=None)

    return jsonify(success=True, data={})


def build_app(in_file="crowdsourcing.csv", num_rel=10, out_dir="./responses", compl_code=None):
    if compl_code is None:
        logger.error("Please use a Prolific completion code!")
        return

    args = Args(in_file=in_file, num_rel=num_rel, out_dir=out_dir, compl_code=compl_code)
    main(args)
    
    return app

def main(args):
    app.args = args
    logger.info(f"Prolific completion code: {app.args.compl_code}")
    load_data(args)
    app.property_idx = 0
