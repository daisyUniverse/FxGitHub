from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import requests
import logging
import os.path

# FXGithub
# An attempt to make github code snippets look good in discord embeds
# Robin Universe [T]
# 05 . 13 . 23

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, filename='fxgithub.log', filemode='w', format='%(message)s')

col = {
    "red"       : "\033[91m",
    "green"     : "\033[92m",
    "yellow"    : "\033[93m",
    "blue"      : "\033[94m",
    "magenta"   : "\033[95m",
    "cyan"      : "\033[96m",
    "white"     : "\033[97m",
    "reset"     : "\033[0m"
}

logging.info(f"{col['green']} <3 FXGithub by Robin Universe started. {col['reset']}")

@app.route('/')
def default():
    return render_template('default.html', message="HELLO. WELCOME TO THE FXGITHUB TESTING INITIATIVE")

@app.route('/<path:subpath>')
def fxgithub(subpath):
    splitpath = subpath.split("/")
    try:
        author  = splitpath[0]
        repo    = splitpath[1]
        action  = splitpath[2]
        branch  = splitpath[3]
        file    = '/'.join(splitpath[4:])
    except:
        logging.warning(f"{col['red']} [ !!! ERROR: ] {subpath} is not a valid github link {col['reset']}" )
        return render_template('default.html', message="Please specify a github link with the format /author/repo/action/branch/file")
    
    if action != "blob":
        return render_template('default.html', message="Please specify a file with the blob action, e.g. /RobinUniverse/FXGithub/blob/main/twitfix.py")

    rawfileurl  = ("https://raw.githubusercontent.com/" + author  + "/" + repo + "/" + branch + "/" + file)
    codefile    = ("/home/robin/fxgithub/static/code/" + author + "_" + repo + "_" + branch + "_" + file.split("/")[-1])
    basefile    = file.split("/")[-1]

    if os.path.isfile( codefile ):
        logging.warning(f"{col['blue']} [ !!! CACHE: ] {basefile} already exists locally {col['reset']}" )
        with open( codefile ) as f:
            r = f.read()
    else:
        logging.info(f"\033[94m [ !!! FRESH: ] {basefile} doesn't exist locally, downloading from github... {col['reset']}")
        r = (requests.get(rawfileurl)).text
        with open(codefile, "w+") as f:
            f.write(r)

    try:
        lines       = (list(request.args.keys())[0]).replace("L","").split("-")
        logging.info(f"{col['green']} [ >>> SERVING: ] {author}/{repo}@{branch} {file} L{str(lines[0])}-{lines[1]} {col['reset']}")
    except:
        lines       = ["1", str(len(str(r).split('\n')))]
        logging.warning(f"{col['red']} [ !!! ERROR: ] Failed to read line number argument. Setting to length of document. (L{lines[0]}-{lines[1]}) {col['reset']}" )

    imagefile   = ("/home/robin/fxgithub/static/img/" + author + "_" + repo + "_" + branch + "_" + file.split("/")[-1].split(".")[0] + "_" + "L" + lines[0] + "-" + lines[1] + ".png" )
    githuburl   = ("https://github.com/" + author + "/" + repo + "/" + action + "/" + branch + "/" + file + "#L" + lines[0] + "-" + lines[1])

    if os.path.isfile( imagefile ):
        logging.warning( f"{col['blue']} [ !!! CACHE: ] {imagefile} already exists locally {col['reset']}" )
    else:
        logging.info( f"{col['green']} [ !!! FRESH: ] {imagefile} doesn't exist locally, creating image... {col['reset']}")
        create_image = subprocess.run(["carbon-now", codefile, "--save-to", "/home/robin/fxgithub/static/img", "--save-as", imagefile.split("/")[-1].replace(".png",""), "--headless", "--start", lines[0], "--end", lines[1]])

    logging.info(f"{col['green']} [ >>> SERVING: ] {author}/{repo}@{branch} {file} L{lines[0]}-{lines[1]} {col['reset']}")

    argstring = (f"Lines {lines[0]}-{lines[1]} of {basefile} from {author}/{repo}@{branch}:\n\n")
    return render_template('default.html', img=("https://fxgithub.com/static/img/" + imagefile.split("/")[-1]), message=argstring, original=githuburl)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0', port=80)
