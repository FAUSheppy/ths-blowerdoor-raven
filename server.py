import flask
import argparse
import glob
import os

import eg_geiss_bauherren as parserBackend

app = flask.Flask("THS-Raven")

@app.route("/")
def root():
    allFiles = []
    for filename in glob.glob("static/files/*.pdf"):
        allFiles.append(parserBackend.load(filename))
    
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