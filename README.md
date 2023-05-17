# FxGithub
An attempt to make discord embeds of github snippets and gists a little nicer

![image](https://github.com/robinuniverse/FxGitHub/assets/12601774/a1cef521-2481-4a2d-86f3-9b7590b0a454)


# HOW TO USE:
1. Go to the page of a file you'd like to share some code of
2. If you just want to embed the whole file, just copy the url and paste it with fx
3. If you want specific lines, shift+click what the first line-number of snipped you'd like to share is
4. Shift+click the last line-number of the snippet you'd like to share
5. In your url bar you should have a link ending in, for example, #L1-L51
6. Copy this url, paste it into discord
7. Change github.com to fxgithub.com and change that last # to a ?
8. Paste
9. Image Get!!

note: seems obvious, but this service doesn't have access to private repositories

## some tidbits
- Works with github gists ( you must provide the author in the url )
- Automatically rejects anything the github api can't access
- The maximum number of lines is 70, if you try to include more than 70 lines, it will truncate the request to simply be 70 lines past the starting point
- If you provide only a filename, it will try to display the entire file ( or at least the first 150 lines of it )
- If you try to use this on a repo base url, it will try to display the readme of whatever the main branch of the repo is
- This works with single-line arguments
- Does NOT currently work with character arguments, and in fact including them may break the request. so if it has C in the query you might need to tweak it
- Automatically rejects any filename containing one of a list of common binary filetypes

This server uses `carbon-now-cli` in order to create a pretty, syntax-highlighted preview image of your desired code

There is still much work to be done! For example, I have not yet implemented a way to parse specific characters (this shows up as C arguments in the URL, and won't work)

This is just a for-fun project, and I do not hold myself liable to keep this up and running forever

## This project DOES save all code passed through it, and images generated. If you don't like that, don't use it.

I save the code passed through the service and images generated for caching purposes. 


Licensed under the [Do What The Fuck You Want Except Use NFTs Public License](https://github.com/robinuniverse/wtfnonpl)

# How to run this yourself
I barely know how I run it myself to be quite honest with you. Good luck!
