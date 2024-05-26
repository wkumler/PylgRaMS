
from lxml import etree
import zlib
import base64
import struct
import math
import numpy as np
import pandas as pd
import os
import time
import re

def grabMzxmlData(filename, grab_what, verbosity=0):
    """Get mass-spectrometry data from an mzXML file

    This function handles the mzXML side of things, reading in files that are
    written in the mzXML format. Much of the code is similar to the mzML format,
    but the xpath handles are different and the mz/int array is encoded as a
    single entry rather than two separate. This function has been exposed
    to the user in case per-file optimization (such as peakpicking or additional
    filtering) is desired before the full data object is returned.

    Parameters
    ----------
    files: A character vector of filenames to read into memory.
    Both absolute and relative paths are acceptable.

    grab_what: What data should be read from the file? Options include
    "MS1" for data only from the first spectrometer or "MS2" for fragmentation
    data. These options can be combined (i.e. `grab_data=["MS1", "MS2"]`) or
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
    data frame.

    """
    if verbosity > 1:
        print(f"\nReading file {os.path.basename(filename)}... ")
        last_time = time.time()

    xml_data = etree.parse(filename)
    output_data = {}
    file_metadata = grabMzxmlEncodingData(xml_data)

    if "MS1" in grab_what:
        if verbosity > 1:
            last_time = timeReport(last_time, "Reading MS1 data...")
        output_data["MS1"] = grabMzxmlMS1(xml_data, file_metadata)

    if "MS2" in grab_what:
        if verbosity > 1:
            last_time = timeReport(last_time, "Reading MS2 data...")
        output_data["MS2"] = grabMzxmlMS2(xml_data, file_metadata)

    if verbosity > 1:
        time_total = round(time.time() - last_time, 2)
        print("Total time:", time_total, "seconds")

    return output_data

def grabMzxmlEncodingData(xml_data):
    ns = {'d1': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.2'}
    peak_metadata = xml_data.xpath('//d1:peaks', namespaces=ns)[0]

    compression_type = peak_metadata.get("compressionType")
    compression = {
        'zlib': 'gzip',
        'zlib compression': 'gzip',
        'no compression': 'none',
        'none': 'none'
    }.get(compression_type, 'none')

    precision = int(peak_metadata.get("precision")) / 8

    byte_order = peak_metadata.get("byteOrder")
    endianness_encoding = {
        'network': 'big'
    }.get(byte_order, None)

    return {
        'compression': compression,
        'precision': precision,
        'endi_enc': endianness_encoding
    }

def grabMzxmlMS1(xml_data, file_metadata):
    ns = {'d1': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.2'}
    ms1_xpath = '//d1:scan[@msLevel="1" and @peaksCount>0]'
    ms1_nodes = xml_data.xpath(ms1_xpath, namespaces=ns)
    
    if not ms1_nodes:
        return pd.DataFrame({'rt': [], 'mz': [], 'int': []})
    
    rt_vals = grabMzxmlSpectraRt(ms1_nodes)
    mzint_vals = grabMzxmlSpectraMzInt(ms1_nodes, file_metadata)

    rt_array = np.array(rt_vals)
    rt_repeat = np.repeat(rt_array, [len(arr) for arr in mzint_vals])
    mzint_flat = np.concatenate(mzint_vals)
    dt_array = np.column_stack((rt_repeat, mzint_flat))
    all_data = pd.DataFrame(dt_array, columns=["rt", "mz", "int"])

    return all_data

def grabMzxmlMS2(xml_data, file_metadata):
    ns = {'d1': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.2'}
    ms2_xpath = '//d1:scan[@msLevel="2" and @peaksCount>0]'
    ms2_nodes = xml_data.xpath(ms2_xpath, namespaces=ns)
    
    if not ms2_nodes:
        return pd.DataFrame({'rt': [], 'premz': [], 'fragmz': [], 'int': [], 'voltage': []})
    
    rt_vals = grabMzxmlSpectraRt(ms2_nodes)
    premz_vals = grabMzxmlSpectraPremz(ms2_nodes)
    volt_vals = grabMzxmlSpectraVoltage(ms2_nodes)
    mzint_vals = grabMzxmlSpectraMzInt(ms2_nodes, file_metadata)

    rt_repeat = np.repeat(rt_vals, [len(arr) for arr in mzint_vals])
    premz_repeat = np.repeat(premz_vals, [len(arr) for arr in mzint_vals])
    volt_repeat = np.repeat(volt_vals, [len(arr) for arr in mzint_vals])
    mzint_flat = np.concatenate(mzint_vals)
    dt_array = np.column_stack((rt_repeat, premz_repeat, mzint_flat, volt_repeat))
    all_data = pd.DataFrame(dt_array, columns=["rt", "premz", "fragmz", "int", "voltage"])

    return all_data

def grabMzxmlSpectraRt(xml_nodes):
    rt_attrs = [node.get("retentionTime") for node in xml_nodes]
    rt_units = set(re.sub(r".*[0-9]", "", rt) for rt in rt_attrs)
    rt_vals = [float(re.sub(r"PT|S", "", rt)) for rt in rt_attrs]
    if "S" in rt_units:
        rt_vals = [rt / 60 for rt in rt_vals]
    return(rt_vals)

def grabMzxmlSpectraMzInt(xml_nodes, file_metadata):
    ns = {'d1': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.2'}
    all_peak_nodes = [node.find(".//d1:peaks", namespaces=ns).text for node in xml_nodes]

    vals = []
    for binary in all_peak_nodes:
        if not binary or len(binary) == 0:
            vals.append(np.empty((0, 2)))  # Empty matrix
            continue
        decoded_binary = base64.b64decode(binary)
        if file_metadata['compression'] == 'none':
            decomp_binary = decoded_binary
        elif file_metadata['compression'] == 'zlib':
            decomp_binary = zlib.decompress(decoded_binary)
        else:
            raise ValueError(f"Unsupported compression type: {file_metadata['compression']}")

        if file_metadata['precision'] == 8:
            fmt = 'd'  # Double precision (64-bit)
        else:
            fmt = 'f'  # Single precision (32-bit)
        if file_metadata['endi_enc'] == 'big':
            endi = '>'
        else:
            endi = '<'

        num_values = len(decomp_binary) // struct.calcsize(fmt)
        final_binary = struct.unpack(f'{endi}{num_values}{fmt}', decomp_binary)
        final_binary = np.array(final_binary).reshape(-1, 2)
        vals.append(final_binary)
    return vals

def grabMzxmlSpectraPremz(xml_nodes):
    premz_xpath = "d1:precursorMz"
    ns = {'d1': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.2'}
    premz_nodes = [node.xpath(premz_xpath, namespaces=ns) for node in xml_nodes]
    premz_nodes = [item for sublist in premz_nodes for item in sublist]
    if not premz_nodes:
        return [None] * len(xml_nodes)
    premz_vals = [float(node.text) for node in premz_nodes]
    return(premz_vals)

def grabMzxmlSpectraVoltage(xml_nodes):
    volt_vals = []
    for node in xml_nodes:
        collision_energy_attr = node.get("collisionEnergy")
        if collision_energy_attr is not None:
            volt_vals.append(float(collision_energy_attr))
        else:
            volt_vals.append(None)
    return(volt_vals)

def timeReport(last_time, text):
    current_time = time.time()
    time_total = round(current_time - last_time, 2)
    print(text, time_total, "seconds")
    return current_time

__all__ = ["grabMzxmlData"]
