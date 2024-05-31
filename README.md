# pylgrams
A Python language gloss of the [RaMS package](https://github.com/wkumler/RaMS) for rapid and intuitive access to mass-spectrometry data. This package parses the open source mass-spectrometry mzML and mzXML file types in Python and returns the retention time, *m/z* ratio, and intensity values to the user as a Pandas data frame. This allows for easy chromatogram extraction and visualization.

The package currently lacks much of the expanded functionality of RaMS and is currently comparable to RaMS v1.0. I don't have plans to expand this much further - for additional functionality, consider using the [rpy2 package](https://rpy2.github.io/) to port the R code directly.

## Installation

`pip install pylgrams`

## Demo

```python
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pylgrams

msdata = pylgrams.grabMSdata("src/pylgrams/example_data/S30657.mzML.gz")
bet_chrom = msdata["MS1"][(msdata["MS1"]["mz"]>118.085) & (msdata["MS1"]["mz"]<118.087)]
bet_chrom = bet_chrom[(bet_chrom["rt"]>7) & (bet_chrom["rt"]<9)]
sns.relplot(bet_chrom, kind="line", x="rt", y="int")
plt.show()

bet_frags = msdata["MS2"][(msdata["MS2"]["premz"]>118.0865) & (msdata["MS2"]["premz"]<118.0867)]
plt.stem(bet_frags["fragmz"], bet_frags["int"], linefmt='-k', markerfmt='ko', basefmt=" ")
plt.show()

dir_path = "src/pylgrams/example_data/"
only_mzML_files_os = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.mzML.gz')]
msdata = pylgrams.grabMSdata(only_mzML_files_os)
bet_chrom = msdata["MS1"][(msdata["MS1"]["mz"]>118.085) & (msdata["MS1"]["mz"]<118.087)]
sns.relplot(bet_chrom, kind="line", x="rt", y="int", hue="filename")
plt.show()
```
