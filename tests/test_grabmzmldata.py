
import pytest
import pandas as pd
from pylgrams import grabMzmlData

# Sample test files (replace these with actual test file paths)
sample_file = "src/pylgrams/example_data/S30657.mzML.gz"

@pytest.fixture
def msdata():
    return grabMzmlData(sample_file, grab_what=["MS1", "MS2", "BPC", "TIC"])

def test_msdata_structure(msdata):
    assert isinstance(msdata, dict), "msdata should be a dictionary"
    assert len(msdata) == 4, "msdata should be of length 4"
    assert msdata.keys() == {"MS1", "MS2", "BPC", "TIC"}, "msdata is named incorrectly"

def test_ms1_structure(msdata):
    ms1_data = msdata["MS1"]
    assert isinstance(ms1_data, pd.DataFrame), "MS1 is not a pd.DataFrame"
    assert list(ms1_data) == ["rt", "mz", "int"], "MS1 is named incorrectly"
    assert len(ms1_data["rt"]) > 0, "No rows present in MS1"
    assert all(ms1_data > 0), "Negative values present in MS1"


def test_ms2_structure(msdata):
    ms2_data = msdata["MS2"]
    assert isinstance(ms2_data, pd.DataFrame), "MS2 is not a pd.DataFrame"
    assert list(ms2_data) == ["rt", "premz", "fragmz", "int", "voltage"], "MS2 is named incorrectly"
    assert len(ms2_data["rt"]) > 0, "No rows present in MS2"
    assert all(ms2_data > 0), "Negative values present in MS2"

def test_bpctic_structure(msdata):
    bpc_data = msdata["BPC"]
    assert isinstance(bpc_data, pd.DataFrame), "BPC is not a pd.DataFrame"
    assert list(bpc_data) == ["rt", "int"], "BPC is named incorrectly"
    assert len(bpc_data["rt"]) > 0, "No rows present in BPC"
    assert all(bpc_data > 0), "Negative values present in BPC"

    tic_data = msdata["TIC"]
    assert isinstance(tic_data, pd.DataFrame), "TIC is not a pd.DataFrame"
    assert list(tic_data) == ["rt", "int"], "TIC is named incorrectly"
    assert len(tic_data["rt"]) > 0, "No rows present in TIC"
    assert all(tic_data > 0), "Negative values present in TIC"

def test_msdata_comp(msdata):
    assert all(msdata["TIC"]["int"] >= msdata["BPC"]["int"])
    assert len(msdata["TIC"]["rt"]) == len(msdata["BPC"]["rt"])
    assert len(msdata["TIC"]["rt"]) <= len(msdata["MS1"]["rt"])

if __name__ == "__main__":
    pytest.main()
