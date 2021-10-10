#!/usr/bin/python3

import flask
import argparse
import glob
import os
from data import BlowerdoorData
import datetime
import os.path
import werkzeug.utils

import eg_geiss_bauherren as parserBackend

app = flask.Flask("THS-Raven")

@app.route("/", methods=["GET", "POST"])
def root():
    if flask.request.method == 'POST':
        fileObj = flask.request.files['file']
        fname = werkzeug.utils.secure_filename(fileObj.filename)
        fullpath = os.path.join('static/files/', fname)
        if not fname.endswith(".pdf"):
            return (405, "Datei ist kein PDF")
        else:
            fileObj.save(fullpath)
            return flask.redirect("/")

    allFiles = []
    loaded = None
    for filename in glob.glob("static/files/*.pdf"):
        try:
            loaded = parserBackend.load(filename)
        except Exception:
            loaded = BlowerdoorData(os.path.basename(filename), os.path.basename(filename), "Fehler", "Fehler", datetime.datetime.now(), datetime.datetime.now())
        allFiles.append(loaded)

    # check duplicates
    duplicateCheckMap = dict()
    for f in allFiles:
        if f.inDocumentDate:
            duplicateCheckMap.update({ f.customer + f.location : f })
    
    for f in allFiles:
        key = f.customer + f.location
        if key in duplicateCheckMap and not f is duplicateCheckMap[key]:
            if f.inDocumentDate <= duplicateCheckMap[key].inDocumentDate:
                f.outdated = True


    return flask.render_template("index.html", listContent=allFiles)

@app.route("/get-file")
def getFile():
    return flask.send_from_directory("static/files/", flask.request.args.get("basename"), mimetype="application/pdf")

@app.before_first_request
def init():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start THS-Raven', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on')
    parser.add_argument('--port', default="5000", \
            help='Port on which flask (this server) will take requests on')
   
    
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)
