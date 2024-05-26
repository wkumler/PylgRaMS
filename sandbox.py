
# !pip install lxml pandas tqdm
from lxml import etree
import zlib
import base64
import struct
import math
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from functools import reduce
import time
from datetime import timedelta


# xml_data = etree.parse("S30657.mzML.gz")
# file_metadata = grabMzmlEncodingData(xml_data)
# grabMzmlMS1(xml_data, file_metadata)
# grabMzmlMS2(xml_data, file_metadata)

grabMzmlData("S30657.mzML.gz", grab_what=["MS1", "MS2"], verbosity=2)

msdata = grabMSdata("S30657.mzML.gz")

msdata = grabMSdata(["S30657.mzML.gz", "LB12HL_AB.mzML.gz"])

msdata = grabMSdata(["LB12HL_AB.mzML.gz", "LB12HL_CD.mzML.gz", "LB12HL_EF.mzML.gz"])


bet_chrom = msdata["MS1"][(msdata["MS1"]["mz"]>118.085) & (msdata["MS1"]["mz"]<118.087)]
# !pip install seaborn
import seaborn as sns
sns.relplot(bet_chrom, kind="line", x="rt", y="int")




from pylgrams import grabMSdataCode
grabMSdataCode.grabMSdata("S30657.mzML.gz")

import pylgrams
msdata = pylgrams.grabMSdata("src/pylgrams/example_data/S30657.mzML.gz")