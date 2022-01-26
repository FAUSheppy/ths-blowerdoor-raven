#!/usr/bin/python3

import flask
import argparse
import glob
import json
import os
from data import BlowerdoorData
import datetime
import os.path
import werkzeug.utils

from sqlalchemy import Column, Integer, String, Boolean, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

import eg_geiss_bauherren as parserBackend

app = flask.Flask("THS-Raven")
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class DocumentStatus(db.Model):
    __tablename__ = "document_status"
    documentName = Column(String, primary_key=True)
    done         = Column(Boolean)

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
            loaded = BlowerdoorData(os.path.basename(filename), os.path.basename(filename),
                            "Fehler", "Fehler", datetime.datetime.now(), datetime.datetime.now())
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

    # get done status #
    statusList = db.session.query(DocumentStatus).all()
    statusDict = dict()
    for docStatus in statusList:
        statusDict.update({ docStatus.documentName  : docStatus.done })
    for bd in allFiles:
        if bd.docName in statusDict:
            bd.done = statusDict[bd.docName]

    # filter which documents to show based on status #
    showStatusArg = flask.request.args.get("showstatus")
    if showStatusArg == "done":
        allFiles = list(filter(lambda bd: not bd.done, allFiles))
    elif showStatusArg == "notdone":
        allFiles = list(filter(lambda bd: bd.done, allFiles))

    return flask.render_template("index.html", listContent=allFiles, statusDict=statusDict)

@app.route("/document-status", methods=["GET", "POST", "DELETE"])
def documentStatus():
    documentName = flask.request.form["documentName"]
    if flask.request.method == "GET":
        status = db.session.query(DocumentStatus).filter(
                        DocumentStatus.documentName == documentName).first()
        return flask.Response(json.dumps(status), 200, mimetype="application/json")
    elif flask.request.method == "POST":
        status = db.session.query(DocumentStatus).filter(
                        DocumentStatus.documentName == documentName).first()

        if status:
            status.done = not status.done
            db.session.add(status)
            db.session.commit()
        else:
            status = DocumentStatus()
            status.documentName = documentName
            status.done = True
            db.session.add(status)
            db.session.commit()

        return flask.redirect("/")
    elif flask.request.method == "DELETE":
        status = db.session.query(DocumentStatus).filter(
                        DocumentStatus.documentName == documentName).first()
        db.session.delete(status)
        db.session.commit()
        return flask.Response("", 200)
    else:
        return ("Bad Request Method", 405)

@app.route("/get-file", methods=["GET", "POST", "DELETE"])
def getFile():
    print(flask.request.args)
    if "delete" in flask.request.args:

        # delete main file #
        fp = os.path.join("static/files/", flask.request.args.get("delete"))
        print(fp)
        os.remove(fp)

        # delete assotiated files #
        # TODO

        # delete the done status #
        status = db.session.query(DocumentStatus).filter(
                        DocumentStatus.documentName == flask.request.args.get("delete")).first()
        if status:
            db.session.delete(status)
            db.session.commit()

        return flask.redirect("/")
    else:
        return flask.send_from_directory("static/files/", 
                        flask.request.args.get("basename"), mimetype="application/pdf")

@app.before_first_request
def init():
    app.config["DB"] = db
    db.create_all()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start THS-Raven', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on')
    parser.add_argument('--port', default="5000", \
            help='Port on which flask (this server) will take requests on')
   
    
    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)
