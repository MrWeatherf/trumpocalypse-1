#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
import subprocess
import sys

Tags = [
	'AltFacts',
	'BabyHands',
	'Commentary',
	'GloriousLeader',
	'HaHa',
	'Hmmm',
	'ILoveWomen',
	'Lawsuit',
	'Misc',
	'Nazi',
	'News',
	'Punch',
	'Satire',
	'ThanksObama',
	'Twitter',
]

def error(msg):
	print 'Error: %s' % (msg)
	sys.exit(1)

def html_escape(str):
	str = str.replace("&", "&amp;")
	str = str.replace("<", "&lt;")
	return str

class Parser():
	"""Build script for Trumpocalypse"""

	def __init__(self):
		self.in_day = False
		self.in_entry = False

		self.validTags = {}
		for t in Tags:
			self.validTags[t] = True
			
		self.day = 0
		self.date = ''
		
		self.reset()

	def reset(self):
		self.title = ''
		self.url = ''
		self.tags = []
		self.desc = ''		
	
	# Process an entire line from the file.
	def process_line(self, line):

		# Process comments.
		m = re.match(r'^#', line)
		if m:
			return

		if line == '':
			if self.in_entry:
				self.write_entry()
				self.reset()
			self.in_entry = False
			return

		m = re.match(r'^DAY (?P<day>\d+): (?P<date>.+)$', line)
		if m:
			self.day = int(m.group('day'))
			self.date = m.group('date')
			self.day_start()
			return

		m = re.match(r'^TITLE: (?P<title>.+)$', line)
		if m:
			self.title = m.group('title')
			self.in_entry = True
			return
			
		m = re.match(r'^URL: (?P<url>.+)$', line)
		if m:
			self.url = m.group('url')
			return

		m = re.match(r'^TAGS: (?P<tags>.+)$', line)
		if m:
			tags = m.group('tags').split(' ')
			for t in tags:
				if not t in self.validTags:
					error('Invalid tag: %s' % t)
			self.tags = tags
			return

		m = re.match(r'^DESC: (?P<desc>.+)$', line)
		if m:
			self.desc = m.group('desc')
			return

		error('Unrecognized line: %s' % line)
					
	def write_html_header(self):
		self.outfile.write('<!DOCTYPE html>\n')
		self.outfile.write('<html lang="en">\n')
		self.outfile.write('<head>\n')
		self.outfile.write('\t<meta charset="utf-8">\n')
		self.outfile.write('\t<meta http-equiv="X-UA-Compatible" content="IE=edge">\n')
		self.outfile.write('\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
		self.outfile.write('\t<title>Trumpocalypse</title></head>\n')
		self.outfile.write('\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">\n')
		self.outfile.write('\t<link rel="stylesheet" type="text/css" href="style.css"/>\n')
		self.outfile.write('</head>\n')
		self.outfile.write('<body>\n')
		self.outfile.write('<div class="container">\n')

		self.outfile.write('<div class="main-title">The Trump Administration</div>\n')
		self.outfile.write('<div class="main-subtitle">Day by Day</div>\n')

	def write_html_footer(self):
		self.outfile.write('</div>\n')
		self.outfile.write('</body>\n')
		self.outfile.write('</html>\n')

	def write_entry(self):
		self.outfile.write('<tr><td class="tag-box">')
		if len(self.tags) == 0:
			error('No tags for: %s' % self.title)
		for t in self.tags:
			self.outfile.write('<span class="tag %s">%s</span> ' % (t, t))
		self.outfile.write('</td><td class="info-box">')
		self.outfile.write('<div class="title"><a href="%s">%s</a></div>' % (html_escape(self.url), html_escape(self.title)))
		self.outfile.write('<div class="desc">%s</div>' % html_escape(self.desc))
		self.outfile.write('</td></tr>\n')
	
	def day_start(self):
		if self.in_day:
			self.day_end()
		self.outfile.write('<div class="day">Day %d</div>\n' % self.day)
		self.outfile.write('<div class="date">%s</div>\n' % html_escape(self.date))
		self.outfile.write('<table>\n')
		self.in_day = True
	
	def day_end(self):
		if self.in_day:
			self.outfile.write('</table>\n')
		self.in_day = False

	def process(self, src, dst):
		if not os.path.isfile(src):
			error('File "%s" doesn\'t exist' % src)

		try:
			infile = open(src, 'r')
		except IOError as e:
			error('Unable to open "%s" for reading: %s' % (src, e))

		try:
			outfile = open(dst, 'w')
		except IOError as e:
			error('Unable to open "%s" for writing: %s' % (dst, e))

		self.outfile = outfile
		self.write_html_header()
		for line in infile:
			line = line.strip()
			self.process_line(line)
		self.day_end()
		self.write_html_footer()

		outfile.close()
		infile.close()
	
def main():
	parser = Parser()
	parser.process('data.txt', 'index.html')
	
if __name__ == '__main__':
	main()
