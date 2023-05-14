from flask import Flask, render_template, request, jsonify
import subprocess
import requests
import random

# FXGithub
# An attempt to make github code snippets look good in discord embeds
# Robin Universe [T]
# 05 . 13 . 23

app = Flask(__name__)

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
    
    lines = (list(request.args.keys())[0]).replace("L","").split("-")
    
    rawfileurl = ("https://raw.githubusercontent.com/" + author  + "/" + repo + "/" + branch + "/" + file)
    r = requests.get(rawfileurl)
    
    codefile = ("/home/robin/fxgithub/static/code/" + file.split("/")[-1])
    imagefile = ("/home/robin/fxgithub/static/img/" + file.split("/")[-1].split(".")[0] + "_" + str(random.randint(1000,9999)))
    githuburl = ("https://github.com/" + author + "/" + repo + "/" + action + "/" + branch + "/" + file + "#L" + lines[0] + "-" + lines[1])
    print(githuburl)
    with open(codefile, "w+") as f:
        f.write(r.text)

    create_image = subprocess.run(["carbon-now", codefile, "--save-to", "/home/robin/fxgithub/static/img", "--save-as", imagefile.split("/")[-1], "--headless", "--start", lines[0], "--end", lines[1]])
    print(create_image)
    basefile = file.split("/")[-1]
    argstring = (f"Lines {lines[0]}-{lines[1]} of {basefile} from {author}/{repo}@{branch}:\n\n")
    return render_template('default.html', img=("https://fxgithub.com/static/img/" + imagefile.split("/")[-1] + ".png"), message=argstring, original=githuburl)

if __name__ == "__main__":
    app.config['SERVER_NAME']='localhost:80'
    app.run(host='0.0.0.0', port=80)
