# PyConcat

Python spectra Concatenation Tool.

This GUI tool is used to concatenate two spectra files into one file.
Features include defining the scaling factor and average number for each spectrum to allow proper weight.
It can also be used to simply perform spectral averages (given that two spectral files have the same frequency range).

## Installation from source & running

```bash
#clone the repository
git clone https://www.github.com/luyaozou/pyconcat
#Install the building tools
python3 -m pip install --upgrade build
#build and install the package
python3 -m build
python3 -m pip install .
#run the program
pycc
```
