## Markdown Website Receiver Script

This script acts as a listener to [GitHub WebHook's push events](https://developer.github.com/v3/activity/events/types/#pushevent), meant to be used alongside [Course Website MD Template](https://github.com/usc-cs/md_template). Whenever connected properly, a push to the `deploy` branch on GitHub will trigger this script, it will:

- fetch the latest version of a website from the repository
- build with jekyll
	- change `site.url` to the `http://bits.usc.edu/***`
- copy the built static webpages to the correct folder
- serve the new site from `http://bits.usc.edu/***`

In order to set up your website, please follow the instructions on the [Template Site](http://bits.usc.edu/_md).

### Structure

For simplicity's sake, the main entry point is `receiver.php`. PHP will handle the validation that a POST request was indeed submitted from GitHub through the secret we have defined with them. Once validated, they'll pass the major lifting to passed to the Pyhton script, `receiver.py`.

`sites.json` defines the list of registered repositories. The key to each object should be the full repository name (`username/reponame`), and it should contain at least one item: `target`, which defines where the compiled repository should be served from. For example, `test_md_website` is being served from `http://bits.usc.edu/test_receive` right now. 

### Installation

#### Tools

Be sure you have jekyll version `2.5.3` or higher as the current `receiver.py` script works with this version.  This may also require installation or `redcarpet` or other needed packages.

#### Config

For security purposes, we do not include the necessary config or secret files in the repository. Instead, they'll be read from a file. There are two config files necessary:

- **`github_account.json`** stores the account information for the bot account used to scrape the repository. Currently, on `parallel05` this is set to `ptzbot`.
- **`secret.php`** stores the secret that is shared with and only with GitHub. This secret is used to verify the origin of a request to our scripts. (Otherwise, anybody would be able to send a POST request to receiver.php and trigger an update for no reason)

Create these two files based on the sample files provided. 

#### Create Folders

The receiver script needs two writable folders: `temp/`, which is used as a temporary space to scrape the repo and build from and `../md/`, where the website will be served from. At the current time, there is no option to configure these paths yet.

**Important!** Make sure the user running these scripts (that'll likely be `www-data`) has write permission to these folders!

#### No 3rd step

That's... pretty much it. Make sure `receiver.php` is reachable externally, and you're all set.

#### One more thing...

You might want to put these in the root directory `.htaccess`:

```htaccess
# Turn on Apache's Rewrite Engine
RewriteEngine On
RewriteBase /

# if md/file exists, then go there
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{DOCUMENT_ROOT}/md/%{REQUEST_URI}/ -d
RewriteRule ^(.+)$ md/$1/ [L]

RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{DOCUMENT_ROOT}/md/%{REQUEST_URI} -f
RewriteRule ^(.+)$ md/$1 [L]
```

This forwards all requests from `domain/path` to `domain/md/path` if the file or directory `/md/path` exists. This allows the script to keep all Jekyll-build websites together in a folder, while avoiding losing pretty URLs.

