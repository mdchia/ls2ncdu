# ls2ncdu
Parser for systems which only have `ls -lR` available

JSON format ref: https://dev.yorhel.nl/ncdu/jsonfmt

## Usage

Output is written to stdout. Takes output from `ls -lR`. The resulting .json file is readable by `ncdu -f`

Example usage for [NCI massdata](https://opus.nci.org.au/display/Help/MASSDATA+User+Guide):

```
mdss ls -lR | ls2ncdu.py > mdss_files.json
ncdu -f mdss_files.txt
```
