# PylgRaMS
A Python language gloss of the [RaMS package](https://github.com/wkumler/RaMS) for rapid and intuitive access to mass-spectrometry data. This package parses the open source mass-spectrometry mzML and mzXML in Python and returns the retention time, *m/z* ratio, and intensity values to the user as a Pandas data frame. This allows for easy chromatogram extraction and visualization.

The package currently lacks much of the expanded functionality of RaMS and is currently comparable to RaMS v1.0. I don't have plans to expand this much further - for additional functionality, consider using the [rpy2 package](https://rpy2.github.io/) to port the R code directly.
