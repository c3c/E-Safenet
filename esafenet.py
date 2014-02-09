# E-Safenet encryption/decryption suite.
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
import os
import random
import simplelzo1x #Self-created safenet-specific module, see simplelzo1x folder.
import struct
import random
import cPickle
import collections
import argparse
import partial_c
import partial_binary

"""
Esafenet: A class to perform encryption/decryption operations on E-Safenet files.
Jan Laan, Cedric Van Bockhaven; 2014
jan.laan@os3.nl, cedric.vanbockhaven@os3.nl
Created for a Research project, Master System and Network Engineering, University of Amsterdam.

This class enables you to encrypt or decrypt files and folders with the E-Safenet algorithm.
It also allows you to generate (not truly) random keys, and find keys using a known-plaintext attack.
"""
class Esafenet:
	

	"""
	Encrypt a given text, with the key given.
	Returns the encrypted text.
	"""
	@staticmethod
	def encrypt_file(text, key):
		
		compressed_bytes = simplelzo1x.compress(text[:512])
		compressed_len = len(compressed_bytes)
		#3 bytes act as checksum for the second 512 bytes of the message. The 1 is static.
		checksum = sum(ord(a) for a in text[512:1024]) | 1 << 24
		padding_end = (512 - compressed_len)

		header = "b" + '\x14' + "#" + "e" + struct.pack('<h', padding_end) + struct.pack('<h', compressed_len) + struct.pack('<I',checksum) + "E-SafeNet" + '\x00\x00\x00' + "LOCK" + '\x00'*(padding_end-28)

		return header + Esafenet.__xor_with_key(compressed_bytes, key) + Esafenet.__xor_with_key(text[512:], key)
	
	"""
	Encrypt an entire folder at the given location, with the key and store it on disk
	"""
	@staticmethod
	def encrypt_folder(folder, key, dest_folder):
		if not os.path.isdir(dest_folder):
			os.mkdir(dest_folder)
	
		for root, dirs, files in os.walk(folder):
			nr = root.replace(folder, "")
			if nr:
				nr += "/"
			for d in dirs:
				if not os.path.isdir(dest_folder + "/" + nr + d):
					os.mkdir(dest_folder + "/" + nr + d)
			for f in files:
				fl = open(root + "/" +  f, "rb")
				enc = Esafenet.encrypt_file(fl.read(), key)
				with open(dest_folder + "/" + nr + f, "wb") as fh:
					fh.write(enc)
			


	"""
	Decrypt a given text, with the key.
	Returns the file's text
	"""
	@staticmethod
	def decrypt_file(text, key):
		plain = ""
		offset = ord(text[4]) | ord(text[5]) << 8  #offset is stored in these 2 bytes in little-endian order.
		decr_header = Esafenet.__xor_with_key(text[offset:512], key)
#		plain_header = ""
		plain_header = simplelzo1x.decompress(decr_header)
		plain_file = Esafenet.__xor_with_key(text[512:], key)
		
		return plain_header + plain_file

	"""
	Xor any text with a given key.
	The key should be an array of byte values.
	An Esafenet key has a length of 512 bytes.
	"""
	@staticmethod
	def __xor_with_key(text, key):
		xored = ""
		for idx, c in enumerate(text):
			keyb = key[idx % len(key)]
			keyb = 0 if keyb is None else keyb
			xored += chr(ord(c) ^ keyb)
		return xored
			
	"""
	Decrypt all files in an entire folder at the given location, with the key and store it on disk
	"""
	@staticmethod
	def decrypt_folder(folder, key, dest_folder):
		if not os.path.isdir(dest_folder):
			os.mkdir(dest_folder)
	
		for root, dirs, files in os.walk(folder):
			nr = root.replace(folder, "")
			if nr:
				nr += "/"
			for d in dirs:
				if not os.path.isdir(dest_folder + "/" + nr + d):
					os.mkdir(dest_folder + "/" + nr + d)
			for f in files:
				fl = open(root + "/" + f, "rb")
				dec = Esafenet.decrypt_file(fl.read(), key)
				with open(dest_folder + "/" + nr + f, "wb") as fh:
					fh.write(dec)


	"""
	Perform a known-plaintext attack. Obtain a key given an encrypted file and its plaintext counterpart.
	The file should be at least 1.5 KB for this to work (1536 bytes)
	Returns the found key
	"""
	@staticmethod
	def find_key(crypted_text, plain_text, key_len=512):
		if len(plain_text) < 512:
			raise EsafenetException("This plaintext attack requires at least 1536 bytes (1.5 KB) of data to work")
		
		text = plain_text[512:1024] #uses this part of the text for plaintext finding. (The first 512 bytes will be compressed, so unusable)
		compare = plain_text[1024:1536] #todo: better comparison (min 512 bytes)
		start = 0

		while(start < len(crypted_text)):
			j = 0
			plain = ""
			key = []
			for i in range(start, len(crypted_text)):
				if(j < key_len):
					key.append(ord(text[j]) ^ ord(crypted_text[i]))
				else:
					plain = plain + chr((ord(crypted_text[i]) ^ key[j % key_len]))
				j += 1

			if compare in plain: 
				key = collections.deque(key)
				key.rotate(start % key_len) #The key is always returned for offset 0
				return key
			else:
				start += 1
		return None #if we haven't returned by the end of the file, no key was found

	"""
	Stores a given key on disk
	"""
	@staticmethod
	def store_key(key, dest_filename):
		with open(dest_filename, "wb") as fh:
			cPickle.dump(key, fh)
	

	"""
	Generate a (not really) random Esafenet key, and store it on disk
	This function generates an array of 512 random bytes, and  stores it.
	"""
	@staticmethod
	def generate_key():
		key = []
		random.seed()
		for i in range(512):
			key.append(random.randint(0, 255))
		return key

	@staticmethod
	def binary_find_key(text):
		return partial_binary.find_binary_key(text)

	@staticmethod
	def text_find_key(infolder, language, outfile):
		partial_c.process_parallel(infolder, language, outfile)

#We even have our own exception!
class EsafenetException(Exception):
	pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Esafenet encryption/decryption/key generation")
	parser.add_argument('a', metavar='action', type=str, help='Action to perform', choices = ['encrypt', 'decrypt', 'encrypt_folder', 'decrypt_folder', 'keygen', 'findkey', 'pattern_decrypt'])
	parser.add_argument('--infile', type=argparse.FileType('rb'), help='Input file', required=False)
	parser.add_argument('--key', type=argparse.FileType('rb'), help='Key file', required=False)
	parser.add_argument('--outfile', type=argparse.FileType('wb'), help='Output file', required=False, default=sys.stdout)
	parser.add_argument('--infolder', type=str, help='Input folder', required=False)
	parser.add_argument('--outfolder', type=str, help='Output folder', required=False)
	parser.add_argument('--comp_file', type=argparse.FileType('rb'), help='Plaintext comparison file used by findkey', required=False)
	parser.add_argument('--type', metavar='pattern_type', type=str, help='Type for pattern decrypt (binary or text)', choices = ['binary', 'text'], required=False)
	parser.add_argument('--language', metavar='text_pattern_language', type=str, help='Language for text pattern decrypt (C, PHP or CS)', choices = ['C', 'PHP', 'CS'], required=False)
	
	args = parser.parse_args()
	
	if args.a == 'keygen':
		if args.outfile == None:
			parser.print_usage()
			print "error: outfile is required for the keygen action"
			sys.exit(1)
		cPickle.dump(Esafenet.generate_key(), args.outfile)

	elif args.a == 'encrypt':
		if args.infile == None:
			parser.print_usage()
			print "error: infile is required for the encrypt action"
			sys.exit(1)

		if args.outfile == None:
			parser.print_usage()
			print "error: outfile is required for the encrypt action"
			sys.exit(1)
		
		if args.key == None:
			parser.print_usage()
			print "error: keyfile is required for the encrypt action"
			sys.exit(1)
		f = Esafenet.encrypt_file(args.infile.read(), cPickle.load(args.key))
		args.outfile.write(f)
		if args.outfile.name != '<stdout>':
			print "Encryption: %d bytes written to %s" % (len(f), args.outfile.name)

	elif args.a == 'encrypt_folder':
		if args.infolder == None or not os.path.isdir(args.infolder):
			parser.print_usage()
			print "error: infolder is required for the encrypt_folder action"
			sys.exit(1)
		 
		if args.outfolder == None:
			parser.print_usage()
			print "error: outfolder is required for the encrypt_folder action"
			sys.exit(1)
		
		if args.key == None:
			parser.print_usage()
			print "error: keyfile is required for the encrypt_folder action"
			sys.exit(1)
		Esafenet.encrypt_folder(args.infolder, cPickle.load(args.key), args.outfolder)

		print "Folder encryption: all written to %s" % args.outfolder
		
	
	elif args.a == 'decrypt':
		if args.infile == None:
			parser.print_usage()
			print "error: infile is required for the decrypt action"
			sys.exit(1)

		if args.outfile == None:
			parser.print_usage()
			print "error: outfile is required for the decrypt action"
			sys.exit(1)
		
		if args.key == None:
			parser.print_usage()
			print "error: keyfile is required for the decrypt action"
			sys.exit(1)
		f = Esafenet.decrypt_file(args.infile.read(), cPickle.load(args.key))
		args.outfile.write(f)
		if args.outfile.name != '<stdout>':
			print "Decryption: %d bytes written to %s" % (len(f), args.outfile.name)
	
	
	elif args.a == 'decrypt_folder':
		if args.infolder == None or not os.path.isdir(args.infolder):
			parser.print_usage()
			print "error: infolder is required for the decrypt_folder action"
			sys.exit(1)
		 
		if args.outfolder == None:
			parser.print_usage()
			print "error: outfolder is required for the decrypt_folder action"
			sys.exit(1)
		
		if args.key == None:
			parser.print_usage()
			print "error: keyfile is required for the decrypt_folder action"
			sys.exit(1)
		Esafenet.decrypt_folder(args.infolder, cPickle.load(args.key), args.outfolder)

		print "Folder decryption: all written to %s" % args.outfolder

	elif args.a == 'findkey':

		if args.infile == None:
			parser.print_usage()
			print "error: infile is required for the find_key action"
			sys.exit(1)
		
		if args.comp_file == None:
			parser.print_usage()
			print "error: comp_file is required for the find_key action"
			sys.exit(1)

		if args.outfile == None:
			parser.print_usage()
			print "error: outfile is required for the decrypt_folder action"
			sys.exit(1)
		key = Esafenet.find_key(args.infile.read(), args.comp_file.read())
		
		cPickle.dump(key, args.outfile)
		if args.outfile.name != '<stdout>':
			print "Succes: key written to %s" % args.outfile.name
	elif args.a == 'pattern_decrypt':
		if args.type == None:
			parser.print_usage()
			print "error: pattern type is required for the pattern_decrypt action"
			sys.exit(1)

		if args.outfile == None:
			parser.print_usage()
			print "error: outfile is required for the pattern_decrypt action (for storing the key)"
			sys.exit(1)

		if args.type == 'binary':
			if args.infile == None:
				parser.print_usage()
				print "error: infile is required for the pattern_decrypt binary action"
				sys.exit(1)
			key = Esafenet.binary_find_key(args.infile.read())
			cPickle.dump(key, args.outfile)
			if args.outfile.name != '<stdout>':
				print "Decryption: key written to %s (%s 0-bytes)" % (args.outfile.name, key.count(0))

		elif args.type == 'text':
			if args.infolder == None:
				parser.print_usage()
				print "error: infolder is required for the pattern_decrypt text action"
				sys.exit(1)
			if args.outfolder == None:
				parser.print_usage()
				print "error: outfolder is required for the pattern_decrypt text action"
				sys.exit(1)
			if args.language == None:
				parser.print_usage()
				print "error: language is required for the pattern_decrypt text action"
				sys.exit(1)
			key = Esafenet.text_find_key(args.infolder, args.language, args.outfile)
