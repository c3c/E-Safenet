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

import itertools
from os.path import commonprefix

# Recipe for pairwise iteration
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)
	
def find_binary_key(text):
	r = text[512:]

	chunks = [r[x:x+512] for x in range(0,len(r),512)]
	store = [None]*512
	for i in range(512):
		store[i] = {}

	for offset in range(512):
		ochunks = [x[offset:] for x in chunks]
		ochunks.sort()

		for s1, s2 in pairwise(ochunks):
			pfx = commonprefix([s1,s2])
			if len(pfx)>16:
				skip = False
				for ofs in store:
					for stored in ofs.keys():
						if pfx in stored:
							skip = True
							break

				if not skip:			
					store[offset][pfx] = store[offset].get(pfx, 0) + 1
					for ofs in range(len(store)):
						for stored in store[ofs].keys():
							if len(stored) < len(pfx) and stored in pfx:
								del(store[ofs][stored])

	key = ['\0']*512
	i = 0

	order = [None]*512

	for ofs in range(len(store)):
		for k in store[ofs].keys():
			if order[len(k)-1] == None:
				order[len(k)-1] = []
			order[len(k)-1].append([k, ofs])

	for o in order:
		if o != None:
			for k, offset in o:
				key[offset:offset+len(k)] = k

	arr = [ord(l) for l in key]
	return arr
