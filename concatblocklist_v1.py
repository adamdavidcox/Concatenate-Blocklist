#!/usr/bin/env python

"""Downloads and concatenates a set list of 
block-list files for use with Transmission"""

#Copyright 2013, Adam David Cox 
#adam.david.cox@gmail.com
#Thanks for PabloG for downloadURL()
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#See <http://www.gnu.org/licenses/> for a copy of the GNU General Public License

#Updated by Thomas Fritzsche 4/5/2013 urllib2.urlopen() edit

import fileinput
import os
import sys
import urllib2
import gzip
import glob

#3..2..1..FIGHT!
  
def helpmessage():
	print """
	Concatblocklist, by Adam Cox
	This program can be used, in conjuction with Transmission,
	to automatically merge sereveral iBlocklist files into a
	single blocklist. 
	When supplied with the file location of a 
	\'blocklist menu\', it will download every individual blocklist 
	(in the p2p format), unpack any gzip files, and concatenate them 
	all into a single blocklist (in the p2p format), placed into 
	Transmission\'s /blocklist/ folder. The \'blocklist menu\' must 
	list 1+ URLS, separated by a newline character.
	All downloaded blocklist files are assumed to be in gzip format,
	as per standards on iblocklist.com. However, any file with the
	\'.txt\' suffix will be treated as a plain-text list in the p2p
	format.
	The suggested use for this program is for it to be run at user
	login, and the \'blocklist menu\' file be stored in 
	/Application Support/Transmission/.
	
	Copyright 2013, Adam David Cox 
	adam.david.cox@gmail.com
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

    See <http://www.gnu.org/licenses/> for a copy of the GNU General Public License
    """
	
def downloadURL(url):

	file_name = url.split('/')[-1]
	try:
		u = urllib2.urlopen(url,None,20)
	except:
		print "\t%s is an invalide URL!" % url
		sys.exit()
	f = open(file_name, 'wb')
	meta = u.info()
	try:
		file_size = int(meta.getheaders("Content-Length")[0])
	except:
		print "\tFile %s contains no data!" % file_name
		sys.exit()
	print "\tDownloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buff = u.read(block_sz)
		if not buff:
			break

		file_size_dl += len(buff)
		f.write(buff)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,

	f.close()

def ungunzip(file_name):
	#Write unzipped data to plaintext file
	print "\t\tformatting file name"
	if file_name[-3:] != '.gz' or file_name[-5:] != '.gzip':
		file_namegz = file_name + '.gz'
	else:
		file_namegz = file_name
	os.rename(file_name, file_namegz)
	print "\t\topening %s" % file_name[:20]
	g = gzip.open(file_namegz, 'rb')
	print "\t\treading %s" % file_name[:20]
	file_content = g.read()
	print "\t\tclosing %s" % file_name[:20]
	g.close()
	
	#Delete gzip-ed files
	print "\t\tremoving %s" % file_name[:20]
	os.remove(file_namegz)
	
	#Write to new file
	print "\t\twriting data to new file"
	n = open(file_name, 'w+')
	n.write(file_content)
	print "\t\tclosing new file\n"
	n.close()

def inputerror():
	print "Run commands must include blocklist menu file location in format:"
	print "$ python %s ~/Libary/Applic*/Transmission/blocklistmenu" % progname
	print "run with option --help for detailed instructions"
	sys.exit()

try:
	progname, blocklistmenu = sys.argv
except:
	progname = sys.argv[0]
	inputerror()

if '-h' in blocklistmenu:
	helpmessage()
	sys.exit()

try:
	blocklistmenu = os.path.expanduser(blocklistmenu)
except:
	inputerror()

if glob.glob(blocklistmenu)==[]:
	print "No blocklist menu exists in that location"
	inputerror()
else:
	blocklistmenu = glob.glob(blocklistmenu)[0]

concat = os.path.expanduser('~/Library/Application Support/Transmission/blocklists/concat')

		
print "Importing blocklist URLs from menu..."

with open(blocklistmenu) as f:
	blocklistURL = f.read().splitlines()

if len(blocklistURL) < 1:
	print "Blocklist menu improperly formatted"
	print "run with option --help for detailed instructions"
	sys.exit()

print "...blocklist URLs imported"

file_namelist = []
print "Downloading and unzipping files..."
for URLtodownload in blocklistURL:
	#Download files
	downloadURL(URLtodownload)
		
	file_name = URLtodownload.split('/')[-1]
	file_namelist.append(file_name)
	
	#Unzip URLtodownload
	if file_name[-3:] != 'txt':
		print "\n\tfile %s is gzip file" % file_name
		ungunzip(file_name)
	else:
		print "\n\tfile %s is text file" % file_name
print "...files downloaded and unzipped"

#Concatenate Text Files
print "Concatenating files into /blocklists/concat..."
print "\topening concat file"
open(concat, "w").close()
e = open(concat, "a+b")
for fileopenmerge in file_namelist:
	print "\topening part file %s" % fileopenmerge[:30]
	n = open(fileopenmerge, 'rb')
	print "\treading data into concat file"
	e.write(n.read())
	print "\tclosing part file %s" % fileopenmerge[:30]
	n.close()
	print "\tremoving part file %s\n" % fileopenmerge[:30]
	os.remove(fileopenmerge)
e.close()
print "...files concatenated into /blocklists/concat"
print "\nDone"
