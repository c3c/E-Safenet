#Statistics on E-Safenet files
#Copyright (C) 2014  Jan Laan, Cedric Van Bockhaven
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; see the file LICENSE. if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#!/usr/bin/python
import pickle
import numpy
import matplotlib.pyplot as plot
from matplotlib import cm
import os
import random

def compare_keys():
	keys = []
	freqs = [0]*256
	for f in os.listdir("./keys"):
		with open("./keys/" + f, "rb") as k:
			keys.append(pickle.load(k))
			#freqs.append([0]*256)
	for i in range(512):
		for j in range(len(keys)):
			freqs[keys[j][i]]+=1

	f2 = [x / len(keys) for x in freqs]
	#frequencies put next to each other
	plot.figure(1)
		#print numpy.arange(256) * len(keys) + i
	plot.bar(numpy.arange(256), freqs, color=cm.jet(1.*i/len(keys)))
	plot.ylabel('byte value frequency')
	plot.xlabel('key byte')
	plot.figure(2)
	#keys  put next to eachother
	for i in range(len(keys)):
		plot.bar(numpy.arange(512) * len(keys) + i, keys[i], color=cm.jet(1.*i/len(keys)))

	plot.ylabel('keybyte value')
	plot.xlabel('keys next to eachother (each color is a key)')

	plot.figure(3)
	for i in range(2):
		plot.plot(keys[i])
	

	key = []
	random.seed()
	for i in range(512):
		key.append(random.randint(0, 255))
	plot.plot(key)
	plot.show()
	
if __name__ == "__main__":
	compare_keys()
