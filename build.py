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
	'Hate',
	#'Hmmm',
	'ILoveWomen',
	'Lawsuit',
	'Mexico',
	'Misc',
	'Nazi',
	'News',
	'Punch',
	'Russia',
	'Satire',
	'Security',
	'Science',
	'ThanksObama',
	'TheWall',
	'Twitter',
]

DaysOfTheWeek = [
	'Sunday',
	'Monday',
	'Tuesday',
	'Wednesday',
	'Thursday',
	'Friday',
	'Saturday',
]

Months = {
	'January': 1,
	'February': 2,
	'March': 3,
	'April': 4,
	'May': 5,
	'June': 6,
	'July': 7,
	'August': 8,
	'September': 9,
	'October': 10,
	'November': 11,
	'December': 12,
}

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

		m = re.match(r'^DAY (?P<day>\d+): (?P<date>[A-Za-z]+ \d+ [A-Za-z]+ \d+)$', line)
		if m:
			self.day = int(m.group('day'))
			self.date = m.group('date')
			date = self.date.split()
			self.day_of_week = date[0]
			self.day_of_month = int(date[1])
			self.month = date[2]
			self.year = int(date[3])
			
			if not self.day_of_week in DaysOfTheWeek:
				error('Invalid day of week: %s' % line)
			if self.day_of_month < 1 or self.day_of_month > 31:
				error('Invalid day of month: %s' % line)
			if not self.month in Months:
				error('Invalid month: %s' % line)
			if self.year < 2017 or self.year > 2017:
				error('Invalid year: %s' % line)
			
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

		self.outfile.write('\t<script>\n')
		self.outfile.write("\t\t(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){\n")
		self.outfile.write("\t\t(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),\n")
		self.outfile.write("\t\tm=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)\n")
		self.outfile.write("\t\t})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');\n")
		self.outfile.write("\t\tga('create', 'UA-1163903-6', 'auto');\n")
		self.outfile.write("\t\tga('send', 'pageview');\n")
		self.outfile.write('\t</script>\n')

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
		self.outfile.write('<div class="day" id="%d">Day %d</div>\n' % (self.day, self.day))
		self.outfile.write('<div class="date" id="%04d-%02d-%02d">%s</div>\n' % (self.year, Months[self.month], self.day_of_month, html_escape(self.date)))
		self.outfile.write('<table class="day-table">\n')
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
	parser.process('data.txt', 'year1.html')
	
if __name__ == '__main__':
	main()
