from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import requests
import logging
import os.path

# FXGithub
# An attempt to make github code snippets look good in discord embeds
# Robin Universe [T]
# 05 . 13 . 23

# Some setup required to make subdomains work
app = Flask(__name__, subdomain_matching=True)
app.config['SERVER_NAME'] = 'fxgithub.com'

# Basic var setup
logging.basicConfig(level=logging.DEBUG, filename='fxgithub.log', filemode='w', format='%(message)s')
badfiles = ".tar"
linelimit = 70

@app.route('/')
def default():
    return render_template("mainsite.html", img="https://fxgithub.com/static/img/robinuniverse_fxgithub_main_2023-05-16T22:36:17Z_README_L1-41.png")

# Bash color codes because fuck you
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

# Base route for the gist subdomain. Required to make the subpath route work
@app.route('/', subdomain="gist")
def gist_home():
    return "Welcome to the Gist subdomain!"

# Route for the gist subdomain with a subpath
@app.route('/<path:subpath>', subdomain="gist")
def gist_subpath(subpath):
    notes = ""
    description = ""
    splitpath = subpath.split("/")
    # Try to parse the url as either a gist id or a gist author and id depending on number of slashes
    try:
        if len(splitpath) == 1:
            id      = splitpath[0]
        else:
            author  = splitpath[0]
            id      = splitpath[1]
    except:
        return render_template('default.html', message="Please specify a valid gist link with an author and an ID")

    # Try to catch bad actors trying to do bad things
    if badfiles in subpath:
        logging.warning(f"{col['red']} [ !!! ERROR: ] {subpath} idiot detection system engaged {col['reset']}" )
        return render_template('default.html', message="Goodnight")
    
    # Try to get the gist info from the github api
    gistapiurl = "https://api.github.com/gists/" + id
    try:
        gistinfo = requests.get(gistapiurl).json()
        #logging.debug(str(gistinfo))
        filecount   = str(len(gistinfo['files']))
        gistfile    = list(gistinfo['files'].keys())[0]
        rawfileurl  = gistinfo['files'][gistfile]['raw_url']
        filename    = gistinfo['files'][gistfile]['filename']
        author      = gistinfo['owner']['login']

        try:
            revisions   = str(len(gistinfo['history']))
        except:
            revisions   = 0
        try:
            comments    = str(gistinfo['comments'])
        except:
            comments    = 0
        try:
            forks       = str(len(gistinfo['forks']))
        except:
            forks       = 0
        try:
            description = gistinfo['description']
        except:
            description = "A Gist on Github"
    except Exception as e:
        logging.error(f"{col['red']} [ !!! ERROR: ] API failure on {author} gist {id} {col['reset']}" )
        logging.error(f"{col['red']} [ !!! ERROR: ] {e} {col['reset']}" )
        return render_template('default.html', message="Github API failed to return a valid response for this gist.")
    
    codefile    = ("/home/robin/fxgithub/static/code/" + author + "_" + id + "_" + filename)

    # Check if the file exists locally
    if os.path.isfile( codefile ):
        logging.warning(f"{col['blue']} [ !!! CACHE: ] {filename} already exists locally {col['reset']}")
        with open( codefile ) as f:
            r = f.read()
    else:
        logging.info(f"\033[94m [ !!! FRESH: ] {filename} doesn't exist locally, downloading from github... {col['reset']}")
        r = (requests.get(rawfileurl)).text
        with open(codefile, "w+") as f:
            f.write(r)

    # Line argument parsing. Kinda complex, but it works. I think.
    try:
        if "-" in list(request.args.keys())[0]:
            lines       = (list(request.args.keys())[0]).replace("L","").split("-")
        else:
            lines[0]       = (list(request.args.keys())[0]).replace("L","")
            lines[1]       = lines[0]
            logging.info(f"{col['green']} [ >>> INFO: ] Only one line ({lines[0]}) designated in arguments {col['reset']}")

        if int(lines[1]) > int(lines[0]) + linelimit:
            logging.warning(f"{col['red']} [ !!! ERROR: ] More than {linelimit} lines requested. truncating... {col['reset']}" )
            notes = f"More than {linelimit} lines requested. truncating..."
            lines[1] = str(int(lines[0]) + linelimit)
        logging.info(f"{col['green']} [ >>> SERVING GIST: ] {filename} L{str(lines[0])}-{lines[1]} {col['reset']}")
    except:
        lines       = ["1", str(len(str(r).split('\n')))]
        if int(lines[1]) > int(lines[0]) + linelimit:
            logging.warning(f"{col['red']} [ !!! ERROR: ] More than {linelimit} lines requested. truncating... {col['reset']}" )
            notes = f"More than {linelimit} lines requested. truncating..."
            lines[1] = str(int(lines[0]) + linelimit)
        logging.warning(f"{col['red']} [ !!! ERROR: ] Failed to read line number argument. Setting to length of document. (L{lines[0]}-{lines[1]}) {col['reset']}" )

    imagefile = ("/home/robin/fxgithub/static/img/" + author + "_" + id + "_" + filename.split(".")[0] + "_" + "L" + lines[0] + "-" + lines[1] + ".png" )
    githuburl = ("https://gist.github.com/" + author + "/" + id + "#file-" + filename)

    # Check if the image exists locally, if not, create it
    if os.path.isfile( imagefile ):
        logging.warning( f"{col['blue']} [ !!! CACHE: ] {imagefile} already exists locally {col['reset']}" )
    else:
        logging.info( f"{col['green']} [ !!! FRESH: ] {imagefile} doesn't exist locally, creating image... {col['reset']}")
        create_image = subprocess.run(["carbon-now", codefile, "--save-to", "/home/robin/fxgithub/static/img", "--save-as", imagefile.split("/")[-1].replace(".png",""), "--headless", "--start", lines[0], "--end", lines[1]])

    # Generate the message and return the template
    revisionString = ""
    forkString = ""
    fileString = ""
    commentsstring = ""

    if int(revisions) > 1:
        revisionString = (f"{revisions}  📝")
    
    if int(forks) > 0:
        forkString = (f"{forks} 🍴")

    if int(filecount) > 1:
        fileString = (f"{filecount}  📁")

    if int(comments) > 0:
        commentsstring = (f"{comments}  💬")

    argstring = (f"{description}\n\nLines {lines[0]}-{lines[1]} of {filename} from {author} on gist:\n\n{notes}\n\n")
    metricstring = (f"{revisionString}  {forkString}  {fileString}  {commentsstring}  ")
    return render_template('default.html', author=author, repo=filename, metricName=metricstring, img=("https://fxgithub.com/static/img/" + imagefile.split("/")[-1]), message=argstring, original=githuburl)

@app.route('/<path:subpath>')
def fxgithub(subpath):
    # Initialize variables
    notes = ""
    barerepo = "False"
    pushdate = "UNKNOWN_DATE"
    splitpath = subpath.split("/")
    logging.info(f"{col['green']} [ >>> REQUEST: ] {subpath} {col['reset']}")

    # Ham-fisted URL parsing
    try:
        author  = splitpath[0]
        repo    = splitpath[1]
        # Get info from the github api
        try:
            repoapiurl  = "https://api.github.com/repos/" + author + "/" + repo
            repoinfo    = requests.get(repoapiurl).json()
            branch      = repoinfo['default_branch']
            pushdate    = repoinfo['pushed_at']
            stars       = repoinfo['stargazers_count']
            watchers    = repoinfo['watchers_count']
            description = repoinfo['description']
            language    = repoinfo['language']
            forks       = repoinfo['forks_count']
            issues      = repoinfo['open_issues_count']
            logging.debug(f"{col['blue']} [ !!! API: ] {author} repo {repo} last pushed at {pushdate} {col['reset']}")
        except:
            logging.warning(f"{col['red']} [ !!! API: ] API failure on {author} repo {repo} {col['reset']}" )
            return render_template('default.html', message="Github API failed to return a valid response for this repo.")
        try:
            # if the info is provided in the url, use it
            action  = splitpath[2]
            branch  = splitpath[3]
            file    = '/'.join(splitpath[4:])
        except:
            # if the url is API valid, but doesn't have the info, assume it's a bare repo
            barerepo = True 
    except:
        # if the url is not API valid, return an error
        logging.warning(f"{col['red']} [ !!! ERROR: ] {subpath} is not a valid github link {col['reset']}" )
        return render_template('default.html', message="Please specify a github link with the format /author/repo/action/branch/file")

    if barerepo == True:
        # if it's a bare repo, assume it's a readme
        action      = "blob"
        file        = "README.md"
        rawfileurl = ("https://raw.githubusercontent.com/" + author  + "/" + repo + "/" + branch + "/" + "README.md")
        codefile    = ("/home/robin/fxgithub/static/code/" + author + "_" + repo + "_" + branch + "_"  + pushdate + "_" + "README.md")
        basefile    = "README.md"
    else:
        # if it's not a bare repo, assume it's a file
        rawfileurl  = ("https://raw.githubusercontent.com/" + author  + "/" + repo + "/" + branch  + "/" + file)
        codefile    = ("/home/robin/fxgithub/static/code/" + author + "_" + repo + "_" + branch + "_" + pushdate + "_" + file.split("/")[-1])
        basefile    = file.split("/")[-1]

    # Check if the file is a binary file
    if badfiles in file:
        logging.warning(f"{col['red']} [ !!! ERROR: ] {subpath} idiot detection system engaged {col['reset']}" )
        return render_template('default.html', message="unsupported filetype")

    if action != "blob":
        return render_template('default.html', message="Please specify a file with the blob action, e.g. /RobinUniverse/FXGithub/blob/main/twitfix.py")

    # Check if the file exists locally, if not, download it
    if os.path.isfile( codefile ):
        logging.warning(f"{col['blue']} [ !!! CACHE: ] {basefile} already exists locally {col['reset']}" )
        with open( codefile ) as f:
            r = f.read()
    else:
        logging.info(f"{col['blue']} [ !!! FRESH: ] {basefile} doesn't exist locally, downloading from github... {col['reset']}")
        resp = (requests.get(rawfileurl))
        if resp.status_code == 200:
            r = resp.text
        else:
            logging.warning(f"{col['red']} [ !!! ERROR: ] {rawfileurl} failed to download from github {col['reset']}" )
            if "README.md" in rawfileurl:
                # This whole rigmarole is because some repos have README.md and some have readme.md, and both work in github but only one works in the raw url
                logging.warning(f"{col['blue']} [ !!! INFO: ] Trying 'readme.md' instead... {col['reset']}" )
                resp = (requests.get(rawfileurl.replace("README.md","readme.md")))
                if resp.status_code == 200:
                    r = resp.text
                else:
                    logging.warning(f"{col['red']} [ !!! ERROR: ] {rawfileurl} failed to download from github {col['reset']}" )
                    return render_template('default.html', message="Failed to download file from github")
            else:
                return render_template('default.html', message="Failed to download file from github.")
            
        with open(codefile, "w+") as f:
            f.write(r)

    try:
        # Overly-complex line argument parsing. Basically just tries to figure out if it's a single line, too big a chunk of text, or a range of lines
        lines = [ "1", "1"]
        lineargs = list(request.args.keys())[0]
        logging.debug(f"{col['green']} [ >>> DEBUG: ] {lineargs} {col['reset']}")
        if "-" in lineargs:
            lines       = lineargs.replace("L","").split("-")
            logging.debug(f"{col['green']} [ >>> DEBUG: ] - detected in args {col['reset']}")
        else:
            lines[0]       = lineargs.replace("L","")
            lines[1]       = lineargs.replace("L","")
            logging.info(f"{col['green']} [ >>> INFO: ] Only one line ({lines[0]}) designated in arguments {col['reset']}")

        if int(lines[1]) > int(lines[0]) + linelimit:
            logging.warning(f"{col['red']} [ !!! ERROR: ] More than {linelimit} lines requested. truncating... {col['reset']}" )
            notes = f"More than {linelimit} lines requested. truncating..."
            lines[1] = str(int(lines[0]) + linelimit)
        logging.info(f"{col['green']} [ >>> SERVING: ] {author}/{repo}@{branch} {file} L{str(lines[0])}-{lines[1]} {col['reset']}")
    except Exception as e:
        lines       = ["1", str(len(str(r).split('\n')))]
        if int(lines[1]) > int(lines[0]) + linelimit:
            logging.warning(f"{col['red']} [ !!! ERROR: ] More than {linelimit} lines requested. truncating... {col['reset']}" )
            notes = f"More than {linelimit} lines requested. truncating..."
            lines[1] = str(int(lines[0]) + linelimit)

        logging.warning(f"{col['red']} [ !!! ERROR: ] Failed to read line number argument. Setting to length of document. (L{lines[0]}-{lines[1]}) {col['reset']}" )

    # Establish filenames and urls
    imagefile   = ("/home/robin/fxgithub/static/img/" + author + "_" + repo + "_" + branch + "_" + pushdate + "_" + file.split("/")[-1].split(".")[0] + "_" + "L" + lines[0] + "-" + lines[1] + ".png" )
    githuburl   = ("https://github.com/" + author + "/" + repo + "/" + action + "/" + branch + "/" + file + "#L" + lines[0] + "-L" + lines[1])

    if os.path.isfile( imagefile ):
        logging.warning( f"{col['blue']} [ !!! CACHE: ] {imagefile} already exists locally {col['reset']}" )
    else:
        logging.info( f"{col['green']} [ !!! FRESH: ] {imagefile} doesn't exist locally, creating image... {col['reset']}")
        create_image = subprocess.run(["carbon-now", codefile, "--save-to", "/home/robin/fxgithub/static/img", "--save-as", imagefile.split("/")[-1].replace(".png",""), "--headless", "--start", lines[0], "--end", lines[1]])

    logging.info(f"{col['green']} [ >>> SERVING: ] {author}/{repo}@{branch} {file} L{lines[0]}-{lines[1]} {col['reset']}")

    headerstring = (f"📝 {repo} from {author}:\n{description}\n\n")
    metricstring = (f"{stars}  ⭐   {forks} 🍴   {issues}  🐛   {watchers}  👀")
    # Grammar modification based on line context
    if lines[0] == lines[1]:
        argstring = (f"{description}\n\nLine {lines[0]} of {basefile} from {branch} branch:\n{notes}")
    else:
        argstring = (f"{description}\n\nLines {lines[0]}-{lines[1]} of {basefile} from {branch} branch:\n{notes}")

    
    # SHIP IT OFF TO MERCURY BOYS
    return render_template('default.html', metricName=metricstring, repo=repo, author=author, img=("https://fxgithub.com/static/img/" + imagefile.split("/")[-1]), message=argstring, original=githuburl)

@app.route('/favicon.ico')
def favicon():
    # Please Stop Spamming My Logs
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/oembed.json') #oEmbed endpoint
def oembedend():
    desc  = request.args.get("desc", None)
    user  = request.args.get("user", None)
    link  = request.args.get("link", None)
    ttype = request.args.get("ttype", None)
    return  oEmbedGen(desc, user, link, ttype)

def oEmbedGen(description, user, video_link, ttype):
    out = {
            "type"          : ttype,
            "version"       : "1.0",
            "provider_name" : "fxGithub by Robin Universe",
            "provider_url"  : "https://github.com/robinuniverse/fxgithub",
            "title"         : description,
            "author_name"   : user,
            "author_url"    : video_link
            }

    return out

if __name__ == "__main__":
    app.run(host='143.42.114.153')
