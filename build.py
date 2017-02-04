#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
import subprocess
import sys

from sets import Set

TagGroups = [
	['Protagonist/Antagonist', [
		'GloriousLeader',
		]],
	['Actors', [
		'Bannon',
		'Conway',
		'Spicer',
		'ThanksObama',
		]],
	['Country', [
		'Canada',
		'Mexico',
		'MiddleEast',
		'Russia',
		'UK',
		]],
	['Topics', [
		'AltFacts',
		'BabyHands',
		'Environment',
		'Ethics',
		'HealthCare',
		'ILoveWomen',
		'Lawsuit',
		'Nazi',
		'Punch',
		'SCOTUS',
		'Security',
		'Science',
		'TheWall',
		'TravelBan',
		]],
	['Category', [
		'Commentary',
		'Misc',
		'News',
		'Satire',
		'Twitter',
		]],
	['Editorial', [
		'HaHa',
		'Hate',
		'Irony',
		]],
]

# Build list of Tags from entries in TagGroups.
Tags = []
for tg in TagGroups:
	(group, taglist) = tg
	for t in taglist:
		Tags.append(t)

DaysOfTheWeek_Map = {
	'Sunday': 0,
	'Monday': 1,
	'Tuesday': 2,
	'Wednesday': 3,
	'Thursday': 4,
	'Friday': 5,
	'Saturday': 6,
}

Months = [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December',
]

# Build map of month name -> month index (1..12).
Months_Map = {}
index = 1
for m in Months:
	Months_Map[m] = index
	index += 1

# Days in each month (index 1..12).
MonthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def error(msg):
	print 'Error: %s' % (msg)
	sys.exit(1)

def html_escape(str):
	str = str.replace("&", "&amp;")
	str = str.replace("<", "&lt;")
	return str

class Parser():
	"""Build script for Trumpocalypse"""

	def __init__(self, src, dst):
		self.in_day = False
		self.in_entry = False

		self.day = None
		self.date = None
		
		self.first_date = None
		self.last_date = None
		
		self.reset_day()

		self.base_name = dst
		
		if not os.path.isfile(src):
			error('File "%s" doesn\'t exist' % src)

		try:
			self.infile = open(src, 'r')
		except IOError as e:
			error('Unable to open "%s" for reading: %s' % (src, e))

		try:
			self.outfile_all = open('%s.html' % dst, 'w')
		except IOError as e:
			error('Unable to open "%s" for writing: %s' % (dst, e))

		self.tagFiles = {}
		for t in Tags:
			try:
				out = 'tag/%s/%s.html' % (t, dst)
				if not os.path.exists(os.path.dirname(out)):
					os.makedirs(os.path.dirname(out))
				self.tagFiles[t] = open(out, 'w')
			except (IOError, OSError) as e:
				error('Unable to open "%s" for writing: %s' % (dst, e))
			
	def reset_day(self):
		self.day_entries = []
		self.day_tags = Set([])
		
		self.reset_entry()
		
	def reset_entry(self):
		self.title = ''
		self.url = ''
		self.tags = []
		self.desc = ''		
	
	def write_calendar(self):
		try:
			out = open('calendar.html', 'w')
		except IOError as e:
			error('Unable to open "calendar.html" for writing: %s' % e)
		
		first_year = 2017
		first_month = 1
		first_day = 20
		last_year = 2017
		last_month = 2
		last_day = 4
		last_display_month = 3
		
		base_path = ''
		self.write_html_header(out, 'Trumpocalypse', base_path)
		self.write_title(out, base_path, 'month')
		out.write('\n')

		# Starting day of week for Jan 2017.
		start_day_of_week = 0
		
		for year in xrange(first_year, last_year+1):
			if year == first_year:
				m_start = first_month
			else:
				m_start = 1
			if year == last_year:
				m_end = last_display_month
			else:
				m_end = 12
				
			out.write('<div class="year">%d</div>\n' % year)
			out.write('\n')
			out.write('<div class="row">\n')
		
			for m in range(m_start, m_end+1):
				out.write('\t<div class="col-md-4">\n')
				d_start = 1
				d_end = MonthDays[m]
				if year == first_year and m == first_month:
					d_start = first_day
				if year == last_year and m == last_month:
					d_end = last_day
				if year == last_year and m > last_month:
					d_start = 0
					d_end = 0
				self.write_calendar_month(out, year, m, start_day_of_week, MonthDays[m], d_start, d_end)
				start_day_of_week += MonthDays[m]
				start_day_of_week %= 7
				out.write('\t</div>\n')

			out.write('</div>\n')
			out.write('\n')
		
		self.write_html_footer(out)
		out.close()

	def write_calendar_month(self, out, year, month, start_day_of_week, num_days, start_day, end_day):
		out.write('\t\t<table class="month-div">\n')
		out.write('\t\t<tr><td colspan=7><span class="month-name" id="%04d-%02d">%s</span></td></tr>\n' % (year, month, Months[month-1]))
		out.write('\t\t<tr>\n')

		column = 0
		day = 1
		
		for x in range(0, start_day_of_week):
			out.write('\t\t\t<td class="month-day disabled">  </td>\n')
			column += 1

		for day in range(1, num_days+1):
			if day < start_day or day > end_day:
				out.write('\t\t\t<td class="month-day disabled">%2d</td>\n' % day)
			else:
				out.write('\t\t\t<td class="month-day"><a href="year1.html#%04d-%02d-%02d">%2d</a></td>\n' % (year, month, day, day))
			column += 1
			if column % 7 == 0:
				out.write('\t\t</tr>\n')
				out.write('\t\t<tr>\n')
		
		for x in range(column % 7, 7):
			out.write('\t\t\t<td class="month-day disabled">  </td>\n')

		out.write('\t\t</tr>\n')
		out.write('\t\t</table>\n')

	
	# Process an entire line from the file.
	def process_line(self, line):

		# Process comments.
		m = re.match(r'^#', line)
		if m:
			return

		if line == '':
			if self.in_entry:
				self.record_entry()
				self.reset_entry()
			self.in_entry = False
			return

		m = re.match(r'^DAY (?P<day>\d+): (?P<date>[A-Za-z]+ \d+ [A-Za-z]+ \d+)$', line)
		if m:
			day = int(m.group('day'))
			date = m.group('date')
			self.day_start(day, date)
			return

		m = re.match(r'^TITLE: (?P<title>.+)$', line)
		if m:
			self.title = m.group('title')
			if self.title[0:4] == 'http':
				error('Invalid title: %s' % self.title)
			self.in_entry = True
			return
			
		if self.in_entry:
			m = re.match(r'^URL: (?P<url>.+)$', line)
			if m:
				self.url = m.group('url')
				if self.url[0:4] != 'http':
					error('Invalid url: %s' % self.url)
				return

			m = re.match(r'^TAGS: (?P<tags>.+)$', line)
			if m:
				tags = m.group('tags').split(' ')
				for t in tags:
					if not t in self.tagFiles:
						error('Invalid tag: %s' % t)
				self.tags = tags
				return

			m = re.match(r'^DESC: (?P<desc>.+)$', line)
			if m:
				self.desc = m.group('desc')
				return

		error('Unrecognized line: %s' % line)
					
	def write_html_headers(self):
		base_path = ''
		self.write_html_header(self.outfile_all, 'Trumpocalypse', base_path)
		self.write_title(self.outfile_all, base_path, 'day')
		
		base_path = '../../'
		for t in Tags:
			out = self.tagFiles[t]
			self.write_html_header(out, 'Trumpocalypse - %s' % t, base_path)
			self.write_title(out, base_path, 'day')
			out.write('<div class="main-entry-info"><span class="tag %s">%s</span></div>\n' % (t, t))

	def write_html_header(self, out, title, base_path):
		out.write('<!DOCTYPE html>\n')
		out.write('<html lang="en">\n')
		out.write('<head>\n')
		out.write('\t<meta charset="utf-8">\n')
		out.write('\t<meta http-equiv="X-UA-Compatible" content="IE=edge">\n')
		out.write('\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
		out.write('\t<title>%s</title></head>\n' % title)
		out.write('\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">\n')
		out.write('\t<link rel="stylesheet" type="text/css" href="%sstyle.css"/>\n' % base_path)

		out.write('\t<script>\n')
		out.write("\t\t(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){\n")
		out.write("\t\t(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),\n")
		out.write("\t\tm=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)\n")
		out.write("\t\t})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');\n")
		out.write("\t\tga('create', 'UA-1163903-6', 'auto');\n")
		out.write("\t\tga('send', 'pageview');\n")
		out.write('\t</script>\n')

		out.write('</head>\n')
		out.write('<body>\n')
		out.write('<div class="container">\n')

	def write_html_footers(self):
		self.write_html_footer(self.outfile_all)
		for t in Tags:
			self.write_html_footer(self.tagFiles[t])

	def write_html_footer(self, out):
		out.write('</div>\n')
		out.write('</body>\n')
		out.write('</html>\n')
	
	def write_title(self, out, base_path, type):
		out.write('<div class="main-title"><a href="%sindex.html">The Trump Administration</a></div>\n' % base_path)
		out.write('<div class="main-subtitle-box">\n')
		if type == 'day':
			out.write('<div class="main-subtitle-side"><a href="%scalendar.html">Month</a></div>\n' % base_path)
			out.write('<div class="main-subtitle">Day by Day</div>\n')
			out.write('<div class="main-subtitle-side"><a href="#">Tag</a></div>\n')
		elif type == 'month':
			out.write('<div class="main-subtitle-side"><a href="%sindex.html">Day</a></div>\n' % base_path)
			out.write('<div class="main-subtitle">Month by Month</div>\n')
			out.write('<div class="main-subtitle-side"><a href="#">Tag</a></div>\n')
		else:
			error('Unexpected title type: %s' % type)
		out.write('</div>\n')

	def write_day(self):
		self.outfile = self.outfile_all
		self.write_day_with_tag(None)
		
		for t in Tags:
			self.outfile = self.tagFiles[t]
			self.write_day_with_tag(t)
	
	def write_day_with_tag(self, tag):
		if tag == None or tag in self.day_tags:
			self.outfile.write('<div class="day" id="%d">Day %d</div>\n' % (self.day, self.day))
			self.outfile.write('<div class="date" id="%04d-%02d-%02d">%s</div>\n' % (self.year, Months_Map[self.month], self.day_of_month, html_escape(self.date)))
			self.outfile.write('<div class="day-table">\n')
		
			for e in self.day_entries:
				title = e[0]
				url = e[1]
				tags = e[2]
				desc = e[3]
				if tag == None or tag in tags:
					self.outfile.write('<div class="row row_padding">')
					self.outfile.write('<div class="col-md-3 tag-box">')
					if tag == None:
						base_path = ''
					else:
						base_path = '../../'
					for t in tags:
						self.outfile.write('<a href="%stag/%s/%s.html"><span class="tag %s">%s</span></a> ' % (base_path, t, self.base_name, t, t))
					self.outfile.write('</div><div class="col-md-9 info-box">')
					self.outfile.write('<div class="title"><a href="%s">%s</a></div>' % (html_escape(url), html_escape(title)))
					self.outfile.write('<div class="desc">%s</div>' % html_escape(desc))
					self.outfile.write('</div></div>\n')

			self.outfile.write('</div>\n')
	
	def record_entry(self):
		if len(self.tags) == 0:
			error('No tags for: %s' % self.title)
		for t in self.tags:
			self.day_tags.add(t)
		self.day_entries.append([self.title, self.url, self.tags, self.desc])
	
	def day_start(self, day, date):
		if self.in_day:
			self.day_end()

		if self.last_date == None:
			self.last_date = date
		self.first_date = date
			
		prev_day = self.day
		if self.date == None:
			prev_date = None
		else:
			prev_date = self.date.split()
		
		self.day = day
		self.date = date
		
		date = self.date.split()
		self.day_of_week = date[0]
		self.day_of_month = int(date[1])
		self.month = date[2]
		self.year = int(date[3])
		
		if prev_day != None and prev_day != day + 1:
			error('Missing day: %d doesn\'t immediately preceed %d' % (day, prev_day))
		if prev_date != None:
			prev_day_of_month = int(prev_date[1])
			if prev_day_of_month != 1 and prev_day_of_month != self.day_of_month + 1:
				error('Bad day of month: %d doesn\'t immediately preceed %d' % (self.day_of_month, prev_day_of_month))

			prev_dow = prev_date[0]
			if DaysOfTheWeek_Map[prev_dow] != (DaysOfTheWeek_Map[self.day_of_week] + 1) % 7:
				error('Bad day of week: %s doesn\'t immediately preceed %s' % (self.day_of_week, prev_dow))
			
		if not self.day_of_week in DaysOfTheWeek_Map:
			error('Invalid day of week: %s' % line)
		if self.day_of_month < 1 or self.day_of_month > 31:
			error('Invalid day of month: %s' % line)
		if not self.month in Months_Map:
			error('Invalid month: %s' % line)
		if self.year < 2017 or self.year > 2017:
			error('Invalid year: %s' % line)
		
		self.in_day = True
	
	def day_end(self):
		if self.in_day:
			self.write_day()
			self.reset_day()
		self.in_day = False

	def process(self):
		self.write_html_headers()

		for line in self.infile:
			line = line.strip()
			self.process_line(line)

		if self.in_entry:
			self.record_entry()
		self.day_end()

		self.write_html_footers()

		self.infile.close()
		self.close_output_files()

	def close_output_files(self):
		self.outfile_all.close()
		for t in Tags:
			self.tagFiles[t].close()
	
def main():
	parser = Parser('data.txt', 'year1')
	parser.process()
	parser.write_calendar()
	
if __name__ == '__main__':
	main()
