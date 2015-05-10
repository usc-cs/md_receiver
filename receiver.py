import json
import sys
import subprocess
import os
import time
from ConfigParser import SafeConfigParser

import smtplib
from email.mime.text import MIMEText

TIMESTAMP = int(time.time())
EMAIL_FROM = 'USC CS Bot <peterzha@usc.edu>'
logs = []

with open('github_account.json', 'r') as file:
	j = json.loads(file.read())
	githubUsername = j['username']
	githubPassword = j['password']

with open('sites.json', 'r') as file:
	sites = json.loads(file.read())

def log(to_log):
	logs.append(to_log)
	return to_log

def shell(command, cwd=None):
	if cwd is None:
		log('/: ' + command)
	else:
		log(cwd + '/: ' + command)

	shell_output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
	
	stdout, stderr = shell_output.communicate()
	if (stdout != ''):
		log(stdout)
	if (stderr != ''):
		log(stderr)

def email(subject, body, recipient):
	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = EMAIL_FROM
	msg['To'] = recipient

	s = smtplib.SMTP('localhost')
	s.sendmail(EMAIL_FROM, [recipient], msg.as_string())
	s.quit()

def replace_line_if_starts_with(filename, prefix, replacement):
	with open(filename, 'r') as file:
		data = file.readlines()

	for i in range(len(data)):
		if data[i].startswith(prefix):
			data[i] = replacement

	with open(filename, 'w') as file:
	  file.writelines(data)


repo_fullname = sys.argv[1]
repo_name = repo_fullname[repo_fullname.index('/')+1:]

if repo_fullname in sites:
	target = sites[repo_fullname]['target']

	git_url = 'https://' + githubUsername + ':' + githubPassword + '@github.com/' + repo_fullname + '.git'
	dir_name = 'temp/' + repo_name + str(TIMESTAMP)

	shell('git clone ' + git_url + ' ' + dir_name)

	# if clone is successful
	if os.path.isdir(dir_name):
		# first update the url in config
		newurl = 'http://bits.usc.edu/' + target
		log('replacing site URL in ' + dir_name + '/_config.yml to ' + newurl)
		replace_line_if_starts_with(dir_name + '/_config.yml', 'url:', "url: '" + newurl + "'\n")

		# build
		shell('jekyll build', dir_name)

		# clean old built directory, and move
		shell('rm -rf *', '../' + target)
		shell('cp -r ' + dir_name + '/_site/* ../' + target)

		# Remove the temporary clone
		shell('rm -rf ' + dir_name)

		# send email
		email('Website deployed for ' + repo_fullname,
			'Successful Deploy!\n\nFull logs:\n\n' + '\n'.join(logs),
			'peter.comgen@gmail.com')
	else:
		email('Clone unsuccessful for ' + repo_fullname,
			'We tried to clone your repository ' + repo_fullname + ', but was unsuccessful. Did you give permission to the bot?\n\nFull logs:\n\n' '\n'.join(logs),
			'peter.comgen@gmail.com')

else:
	email('Repository ' + repo_fullname + 'not registered',
			'We tried to deploy your repository ' + repo_fullname + ', but was unsuccessful. Have you registered your site with the Markdown service?',
			'peter.comgen@gmail.com')

print logs
