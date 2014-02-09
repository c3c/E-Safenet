/*
  CPLEX model for maximizing printable characters
  Representation as a binary integer programming problem

  Upside: additional constraints can be specified eg. checksum validity.
  Downside: slow. (perhaps other solvers perform better for BIPs?)

  Copyright (C) 2014  Jan Laan, Cedric Van Bockhaven
  
  ----

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program; see the file LICENSE. if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/

// Data

int checksum = ...; // integer checksum
int encrypted_len = ...;
range crange = 0..encrypted_len-1;
int encrypted[crange] = ...; // integer representation of encrypted data

// Decision variables

dvar boolean ckey[0..511][0..7];
dvar boolean plain[crange][0..7];
dvar boolean cipher[crange][0..7];

// Decision expressions

dexpr int plains[i in crange] = sum(b in 0..7) plain[i,b]*ftoi(pow(2,b));

// Objective

maximize sum(i in crange) ((plains[i] >= 32 && plains[i] <= 126)
             || plains[i] == 9 || plains[i] == 10 || plains[i] == 13);

// Subject to

constraints{
    forall (i in crange, b in 0..7) {
        (cipher[i,b] != ckey[i%512,b]) == plain[i,b];
        cipher[i,b] == (encrypted[i] div ftoi(pow(2,b))) % 2;
    }
    sum(i in 0..511) plains[i] == checksum;
}  

// Post-processing

execute {
    var out = ""
    for (var i = 0; i < encrypted_len; i++) {
        if (plains[i] >= 32 && plains[i] <= 126) {
            out += String.fromCharCode(plains[i])
        } else { out+= "?"}
        if (i % 512 == 511) out+="\n";
    }
    writeln("Res: " + out);
}

