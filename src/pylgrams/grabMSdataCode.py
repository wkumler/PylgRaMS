
from lxml import etree
import pandas as pd
import os
from tqdm import tqdm
import time
from .grabMzmlFunctions import grabMzmlData
from .grabMzxmlFunctions import grabMzxmlData

def grabMSdata(files, grab_what="everything", verbosity=None):
    """Grab mass-spectrometry data from file(s)

    The main `pylgrams` function. This function accepts a list of the files that will
    be read into working memory and returns a list of `data.table`s
    containing the requested information. What information is requested is
    determined by the `grab_what` argument, which can include MS1 or MS2
     information. This function serves as a wrapper around both
    `grabMzmlData` and `grabMzxmlData` and handles multiple files, but those two
    have also been exposed to the user in case super-simple handling is desired.
    Retention times are reported in minutes, and will be converted automatically
    if they are encoded in seconds.

    Parameters
    ----------
    files: A character vector of filenames to read into memory.
    Both absolute and relative paths are acceptable.

    grab_what: What data should be read from the file? Options include
    "MS1" for data only from the first spectrometer, "MS2" for fragmentation
    data, "BPC" for a base peak chromatogram, or "TIC" for a total ion chromatogram.
    These options can be combined (i.e. `grab_data=["MS1", "MS2"]`) or
    this argument can be set to "everything" to extract all of the above.

    verbosity: Three levels of processing output to the console are
    available, with increasing verbosity corresponding to higher integers. A
    verbosity of zero means that no output will be produced, useful when
    wrapping within larger functions. A verbosity of 1 will produce a progress
    bar that updates after each file is read. A verbosity of 2 or higher will
    produce timing output for each individual file read in. The default, NULL,
    will select between 1 and 2 depending on the number of files being read: if
    a single file, verbosity is set to 2; if multiple files, verbosity is set
    to 1.

    Returns
    -------
    A list of Pandas data frames, each named after the arguments requested in
    grab_what. E.g. ["MS1"] contains MS1 information, ["MS2"] contains fragmentation
    info, etc. MS1 data has four columns: retention time (rt), mass-to-charge
    (mz), intensity (int), and filename. MS2 data has six: retention time (rt),
    precursor m/z (premz), fragment m/z (fragmz), fragment intensity (int),
    collision energy (voltage), and filename. Data
    requested that does not exist in the provided files (such as MS2 data
    requested from MS1-only files) will return an empty (length zero)
    data frames. The data frames extracted from each of the individual files are
    collected into one large table.

    """
    if not files:
        raise ValueError("No files provided")
    if isinstance(files, str):
        files=[files]
    
    if grab_what=="everything":
        grab_what = ["MS1", "MS2", "BPC", "TIC"]

    if verbosity is None:
        verbosity = 2 if len(files) == 1 else 1
    
    all_file_data = {}
    if verbosity > 0:
        if len(files) >= 2:
            pb = tqdm(total=len(files))
        start_time = time.time()
    
    for file in files:
        filename = os.path.basename(file)
        if '.mzml' in filename.lower():
            out_data = grabMzmlData(filename=file, grab_what=grab_what, verbosity=verbosity)
        elif '.mzxml' in filename.lower():
            out_data = grabMzxmlData(filename=file, grab_what=grab_what, verbosity=verbosity)
        else:
            raise ValueError(f"Unable to determine file type for {filename}")
        
        out_data["MS1"]["filename"] = filename
        out_data["MS2"]["filename"] = filename
        out_data["BPC"]["filename"] = filename
        out_data["TIC"]["filename"] = filename
        all_file_data[filename] = out_data
        
        if verbosity > 0 and len(files) >= 2:
            pb.update(1)

    all_file_data_output = {}
    all_file_ms1 = [file_data['MS1'] for file_data in all_file_data.values() if 'MS1' in file_data]
    all_file_data_output["MS1"] = pd.concat(all_file_ms1, ignore_index=True)
    all_file_ms2 = [file_data['MS2'] for file_data in all_file_data.values() if 'MS2' in file_data]
    all_file_data_output["MS2"] = pd.concat(all_file_ms2, ignore_index=True)
    all_file_bpc = [file_data['BPC'] for file_data in all_file_data.values() if 'BPC' in file_data]
    all_file_data_output["BPC"] = pd.concat(all_file_bpc, ignore_index=True)
    all_file_tic = [file_data['TIC'] for file_data in all_file_data.values() if 'TIC' in file_data]
    all_file_data_output["TIC"] = pd.concat(all_file_tic, ignore_index=True)
    if verbosity > 0:
        if len(files) >= 2:
            pb.close()
        time_total = round(time.time() - start_time, 2)
        print("Total time:", time_total, "seconds")
    return all_file_data_output

__all__ = ["grabMSdata", "grabMzmlData", "grabMzxmlData"]