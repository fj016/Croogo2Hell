# Croogo2Hell
## Introduction

Exploit script for Croogo =<2.3.2, you can find the linked blog post [here](https://fj016.fr/posts/useless_exploit/)

## Installation

```bash
git clone https://github.com/fj016/Croogo2Hell.git
cd Croogo2Hell
pip install -r requirements.txt
```

You can then run the script :
```bash
$ python Croogo2Hell.py --help
usage: Croogo2Hell.py [-h] --url URL --user USER [--pool POOL] [--output OUTPUT] [--offset OFFSET]

Croogo2Hell

options:
  -h, --help       show this help message and exit
  --url URL        Domain name of the target (without https://)
  --user USER      Username of the account we are attacking
  --pool POOL      NTP pool to use (default to europe.pool.ntp.org)
  --output OUTPUT  Output filename, default to tokenslist.txt (overwrote if already exist)
  --offset OFFSET  Time offset to generate the initial cracking list from the known account. Default to 0.7 (1.4 mil.
                   hashes) (Usually don't need to adjust this, if the script can't find any offset, try changing the
                   ntp server to one closer one to target, or increment this, but be careful here, small increase
                   could lead to really huge number generated (0.01-0.05) increment recommended)
```
