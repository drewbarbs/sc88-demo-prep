Floating around on the internet are demo tracks for the Roland SC-88, with names
`Y4002_0x.MID` (`x <- {1..7}`). Most of these files have more than 16 parts,
requiring the simultaneous use of 2 MIDI ports. However, the files contain no
"MIDI Port" or "Device Name" events to direct players to split the load.
Since `aplaymidi` supports the "MIDI Port" event, this script prepends every "PartB" track in
the input file with one, and saves the resulting file as `<infile>-split.MID`.

E.g. to play Y4002_02.MID ("Myth" (C) 1994 Roland Corporation):
```sh
$ ./split_channels.py Y4002_02.MID
$ aplaymidi -p<1st_port>,<2nd_port> Y4002_02-split.MID
```
