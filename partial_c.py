# Probable plaintext decryption of XOR-encrypted files with a key of 512 bytes (for E-Safenet)
# Copyright (C) 2014  Jan Laan, Cedric Van Bockhaven
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file LICENSE. if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import sys
import pickle
from collections import defaultdict
import os
import re
from multiprocessing import Pool

keyword_lists = {}
keyword_lists['C'] = [
"return ",
"return;",
"#include ",
"#DEFINE ",
"#define ",
"#IFDEF",
"static void",
"const char",
"const",
"char *",
"struct",
"extern",
"static",
"      ",
"        ",
"malloc",
"printf",
"sprintf",
"stdio.h",
"Copyright",
"GNU General Public License"]

keyword_lists['PHP'] = [
"this",
"array(",
"function ",
"return ",
"return;",
"public ",
"<?php",
"class ",
"false",
"true",
"null",
"      ",
"        ",
"Copyright"
]

keyword_lists['CS'] = [
"private void InitializeComponent",
"private System.Windows.Forms",
"static void Main(string[] args)",
"private void",
"public void",
"this.",
"public ",
"        ",
"private "
]

open_files = []

def gen():
	for k in keywords:
		yield k

def is_allowed_char(c):
	o = ord(c)
	#Printable character range (and tab, newline, carriage return)
	return (o >= 32 and o <= 126) or o == 9 or o == 10 or o == 13

def is_allowed_string(s):
	for c in s:
		if not is_allowed_char(c):
			return False
	return True

def read_input(dir):
	for root, dirs, files in os.walk(dir):
		for f in files:
			l = open(root + "/" + f).read()
			open_files.append(l)

def xor_one_keyword(keyword):
	#create dictionary for this keyword
	safenet_key = defaultdict(defaultdict)
	for i in range(512):
		safenet_key[i] = defaultdict(int)
	for text in open_files:
		for i in range(512,len(text) - len(keyword)):
			keypart = []
			offset = i % 512
			for idx in range(len(keyword)):
				keypart.append(ord(keyword[idx]) ^ ord(text[i+idx]))
			#Check this keyword + position at all offsets
			safenet_key = offset_key(offset, i, text, keypart, safenet_key)
	return safenet_key

def offset_key(offset, start, text, key, safenet_key):
	total = 0
	match = 0

	for i in range(offset + 512, len(text)-len(key), 512):
		if i is not start:
			total += 1
			(rval, res) = decrypt_part(key, text[i:i+len(key)])
			if(rval):
				match += 1
			else:
				return safenet_key #early exit if we have a non-match
	#We haven't gotten to an early exit
	print "Match found!! offset: %d, start: %d, key; %s" % (offset, start, key)
	for j in range(len(key)):
		safenet_key[(offset+j)%512][key[j]] += 1
	return safenet_key

# assumes text is the same length as key
def decrypt_part(key, text):
	decrypted = ""
	count = 0
	for idx in range(len(key)):
		dc = chr(key[idx] ^ ord(text[idx]))
		if(is_allowed_char(dc)):
			count += 1
		decrypted += dc
	if(count == len(key)):
		return (True, decrypted)
	return (False, decrypted)

def xor_keywords():
	for k in keywords:
		print "Using keyword: %s, (%d)\n" % (k, len(k));
		xor_one_keyword(k)

def format_key(safenet_key):
	out = [None]*512
	for k, v in safenet_key.items():
		largest = 0
		for k2, v2 in v.items():
			if v2 > largest:
				largest = v2
				out[k] = k2
	return out

def compare_keys(safenet_key, comp_key):
	key = format_key(safenet_key)
	match = 0
	nones = 0
	for i in range(len(key)):
		if(key[i] == comp_key[i]):
			match += 1
		if(key[i] == None):
			nones += 1
	print "Matches: %d, nones: %d, Matches + nones: %d"% (match, nones, match+nones)

def process():
	read_input()
	xor_keywords()
	print format_key()
	compare_keys()

def process_parallel(infolder, language, outfile):
	read_input(infolder)
	keywords = keyword_lists[language]

	final_safenet_key = defaultdict(defaultdict)
	for o in range(512):
		final_safenet_key[o] = defaultdict(int)
	p = Pool(4)

	for kw in keywords:
		res_key = p.apply_async(xor_one_keyword, (kw,))
		res_key = res_key.get()
		for k, v in res_key.items():
			for k2, v2 in v.items():
				final_safenet_key[k][k2] += v2
	p.close()
	p.join()
	print final_safenet_key.items()
	k= format_key(final_safenet_key)
	pickle.dump(k, outfile)
	

if __name__ == "__main__":
	process_parallel(sys.argv[1], "PHP", sys.argv[2])
