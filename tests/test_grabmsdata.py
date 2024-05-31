
import pytest
import pandas as pd
import os
from pylgrams import grabMSdata

sample_files = ["src/pylgrams/example_data/LB12HL_AB.mzML.gz",
     "src/pylgrams/example_data/LB12HL_AB.mzXML.gz",
     "src/pylgrams/example_data/LB12HL_CD.mzML.gz",
     "src/pylgrams/example_data/LB12HL_EF.mzML.gz",
     "src/pylgrams/example_data/S30657.mzML.gz",
     "src/pylgrams/example_data/S30657.mzXML.gz"]

msdata = grabMSdata(sample_files, grab_what=["MS1", "MS2", "BPC", "TIC"])

def test_msdata_structure():
    assert isinstance(msdata, dict), "msdata should be a dictionary"
    assert len(msdata) == 4, "msdata should be of length 4"
    assert msdata.keys() == {"MS1", "MS2", "BPC", "TIC"}, "msdata is named incorrectly"

def test_ms1_structure():
    ms1_data = msdata["MS1"]
    assert isinstance(ms1_data, pd.DataFrame), "MS1 is not a pd.DataFrame"
    assert list(ms1_data) == ["rt", "mz", "int", "filename"], "MS1 is named incorrectly"
    assert len(ms1_data["rt"]) > 0, "No rows present in MS1"
    assert all(ms1_data.drop("filename", axis=1) > 0), "Negative values present in MS1"


def test_ms2_structure():
    ms2_data = msdata["MS2"]
    assert isinstance(ms2_data, pd.DataFrame), "MS2 is not a pd.DataFrame"
    assert list(ms2_data) == ["rt", "premz", "fragmz", "int", "voltage", "filename"], "MS2 is named incorrectly"
    assert len(ms2_data["rt"]) > 0, "No rows present in MS2"
    assert all(ms2_data.drop("filename", axis=1) > 0), "Negative values present in MS2"

def test_bpctic_structure():
    bpc_data = msdata["BPC"]
    assert isinstance(bpc_data, pd.DataFrame), "BPC is not a pd.DataFrame"
    assert list(bpc_data) == ["rt", "int", "filename"], "BPC is named incorrectly"
    assert len(bpc_data["rt"]) > 0, "No rows present in BPC"
    assert all(bpc_data.drop("filename", axis=1) > 0), "Negative values present in BPC"

    tic_data = msdata["TIC"]
    assert isinstance(tic_data, pd.DataFrame), "TIC is not a pd.DataFrame"
    assert list(tic_data) == ["rt", "int", "filename"], "TIC is named incorrectly"
    assert len(tic_data["rt"]) > 0, "No rows present in TIC"
    assert all(tic_data.drop("filename", axis=1) > 0), "Negative values present in TIC"

def test_multifile_things():
    assert msdata["MS1"]["filename"].unique().tolist() == [os.path.basename(filename) for filename in sample_files]
    assert len(msdata["MS1"]["filename"].unique()) == len(sample_files)


if __name__ == "__main__":
    pytest.main()
