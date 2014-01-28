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
import matplotlib.pyplot as plot
import numpy
import sys 
import collections

f = open(sys.argv[1], "rb")

text = f.read()
l = [ord(c) for c in text]
acs = []
for i in range(490, 530):
	la = collections.deque(l)
	la.rotate(i)
	ac = numpy.correlate(l, la)
	print i
	print ac
	acs.append(ac[0])
	
plot.bar(range(1025),acs)

plot.xlabel("ciphertext shift in bytes", fontsize=30)
plot.ylabel("autocorrelation", fontsize=30)
plot.tick_params(axis='both', which='major', labelsize=30)
#plot.acorr(l)
plot.show()
