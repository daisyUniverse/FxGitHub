from flask import Flask, render_template, request, jsonify
import subprocess
import requests
import random
import os.path

# FXGithub
# An attempt to make github code snippets look good in discord embeds
# Robin Universe [T]
# 05 . 13 . 23

app = Flask(__name__)

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

@app.route('/')
def default():
    return render_template('default.html', message="HELLO. WELCOME TO THE FXGITHUB TESTING INITIATIVE")

@app.route('/<path:subpath>')
def fxgithub(subpath):
    splitpath = subpath.split("/")
    author = splitpath[0]
    repo = splitpath[1]
    action = splitpath[2]
    branch = splitpath[3]
    file = '/'.join(splitpath[4:])
    
    if action != "blob":
        return render_template('default.html', message="Please specify a file with the blob action, e.g. /RobinUniverse/FXGithub/blob/main/twitfix.py")
    
    if "L" not in (list(request.args.keys())[0]):
        return render_template('default.html', message="Please specify lines to show with the L parameter, e.g. /RobinUniverse/FXGithub/blob/main/twitfix.py?L1-10")
    
    lines       = (list(request.args.keys())[0]).replace("L","").split("-")
    rawfileurl  = ("https://raw.githubusercontent.com/" + author  + "/" + repo + "/" + branch + "/" + file)
    codefile    = ("/home/robin/fxgithub/static/code/" + file.split("/")[-1])
    imagefile   = ("/home/robin/fxgithub/static/img/" + file.split("/")[-1].split(".")[0] + "_" + "L" + lines[0] + "-" + lines[1] + ".png" )
    githuburl   = ("https://github.com/" + author + "/" + repo + "/" + action + "/" + branch + "/" + file + "#L" + lines[0] + "-" + lines[1])
    basefile    = file.split("/")[-1]

    if os.path.isfile( codefile ):
        print(f"{col['blue']} [ !!! CACHE: ] {basefile} already exists locally {col['reset']}" )
        with open("/home/robin/fxgithub/static/code/" + file.split("/")[-1] ) as f:
            r = f.readlines()
    else:
        print(f"\033[94m [ !!! FRESH: ] {basefile} doesn't exist locally, downloading from github... {col['reset']}")
        r = (requests.get(rawfileurl)).text
        with open(codefile, "w+") as f:
            f.write(r)
    
    if os.path.isfile( imagefile ):
        print( f"{col['blue']} [ !!! CACHE: ] {imagefile} already exists locally {col['reset']}" )
    else:
        print( f"{col['green']} [ !!! FRESH: ] {imagefile} doesn't exist locally, creating image... {col['reset']}")
        create_image = subprocess.run(["carbon-now", codefile, "--save-to", "/home/robin/fxgithub/static/img", "--save-as", imagefile.split("/")[-1].replace(".png",""), "--headless", "--start", lines[0], "--end", lines[1]])

    print(f"{col['green']} [ >>> SERVING: ] {author}/{repo}@{branch} {file} L{lines[0]}-{lines[1]} {col['reset']}")

    argstring = (f"Lines {lines[0]}-{lines[1]} of {basefile} from {author}/{repo}@{branch}:\n\n")
    return render_template('default.html', img=("https://fxgithub.com/static/img/" + imagefile.split("/")[-1]), message=argstring, original=githuburl)

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0', port=80)
