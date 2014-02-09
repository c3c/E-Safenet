E-Safenet
=========

This GitHub repository contains files that assist in cryptanalytic attacks on E-Safenet encryption.
Several attacks were developed that may partially or fully recover E-Safenet encryption keys.

 * Known-plaintext attack
 * Probable-plaintext attack
   * Against source code files
   * Against binary files
 * Ciphertext-only attack

## Python scripts

The python scripts provided can be used to encrypt and decrypt using the E-Safenet encryption, or to extract encryption keys.

Two main files are available:

 * [**esafenet.py**](esafenet.py): command-line interface to _known-plaintext_ and _probable-plaintext_ attacks
 * [**esafenet_gui.py**](esafenet_gui.py): GUI interface for the _ciphertext-only_ attack

##### Setup

Prior to using these scripts, the simplelzo1x module has to be compiled first.
This module provides an interface to the LZO v1.00 compression library.

```
cd simplelzo1x && sudo python setup.py install
```

More information about the library can be found in the [README](simplelzo1x/README) file in the simplelzo1x directory.

### esafenet.py

```none
usage: esafenet.py [-h] [--infile INFILE] [--key KEY] [--outfile OUTFILE]
                   [--infolder INFOLDER] [--outfolder OUTFOLDER]
                   [--comp_file COMP_FILE] [--type pattern_type]
                   [--language text_pattern_language]
                   action

E-safenet encryption/decryption/key generation

positional arguments:
  action                Action to perform
                        Should be one of ['encrypt', 'decrypt', 'encrypt_folder', 
                        'decrypt_folder', 'keygen', 'findkey', 'pattern_decrypt']

optional arguments:
  -h, --help            show this help message and exit
  --infile INFILE       Input file
  --key KEY             Key file
  --outfile OUTFILE     Output file
  --infolder INFOLDER   Input folder
  --outfolder OUTFOLDER
                        Output folder
  --comp_file COMP_FILE
                        Plaintext comparison file used by findkey
  --type pattern_type   Type for pattern decrypt (binary or text)
  --language text_pattern_language
                        Language for text pattern decrypt (C, PHP or CS)
```

##### Examples

 * Recovering the encryption key of a binary file (probable-plaintext attack):

```
$ python esafenet.py pattern_decrypt --type binary --infile encrypted.xls --outfile key.dat
Decryption: key written to key.dat (4 0-bytes)
```

 * Decrypting an E-Safenet file using a provided key:
```
$ python esafenet.py decrypt --infile encrypted.xls --key key.dat --outfile decrypted.xls
Decryption: 153400 bytes written to decrypted.xls
```

 * Recovering the key using the known-plaintext attack:
```
$ python esafenet.py findkey --infile encrypted.xls --comp_file decrypted.xls --outfile key.dat
Succes: key written to key.dat
```

 * Recovering the encryption key of source code files (probable-plaintext attack, C#):
```
$ python esafenet.py pattern_decrypt --type text --infolder srcfiles --outfolder /tmp --language CS --outfile key.dat
Match found!! ...
```

##### Troubleshooting

If you get errors/crashes, they are probably caused by the LZO compression library. The first 512 bytes of an E-Safenet encrypted file are compressed. When using a wrong key, decompression may fail and lead to a crash.
You can temporarily disable decompression of the first block by changing the *plain_header* variable in esafenet.py to an empty string:

```
             plain_header = ""
#            plain_header = simplelzo1x.decompress(decr_header)
```

### esafenet_gui.py

The GUI app **esafenet_gui.py** can be used for the ciphertext-only attack.
More information about this attack can be found in the research paper.

1. menu -> Open folder or file, select an E-Safenet file, or a folder containing only E-Safenet files **encrypted with the same key**.
2. menu -> Analyze, analyzes the files, tries to maximize plaintext in the file(s), as described in the report.

Note: The analyze step may take some time (15s for 200kB on my 5y/o laptop, displaying results in thhe grid takes even longer...)

Results are displayed as-is, this program is not complete. Feel free to do with it as you see fit.

![COA tool](../resources/coatool.png?raw=true)

## CPLEX model

For the mathematical implementation of the ciphertext-only attack, [cplex_coa.mod](cplex_coa.mod) provides a CPLEX model for the Binary Integer Programming problem that represents the maximization of printable characters in an E-Safenet encrypted document.

## Credits

The code was released under the GPLv2 license.
