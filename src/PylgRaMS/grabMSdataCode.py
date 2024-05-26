
def grabMSdata(files, grab_what="everything", verbosity=None):
    if not files:
        raise ValueError("No files provided")
    if isinstance(files, str):
        files=[files]
    
    if(grab_what=="everything"):
        grab_what = ["MS1", "MS2"]

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
        else:
            raise ValueError(f"Unable to determine file type for {filename}")
        
        out_data["MS1"]["filename"] = filename
        out_data["MS2"]["filename"] = filename
        all_file_data[filename] = out_data
        
        if verbosity > 0 and len(files) >= 2:
            pb.update(1)

    all_file_data_output = {}
    all_file_ms1 = [file_data['MS1'] for file_data in all_file_data.values() if 'MS1' in file_data]
    all_file_data_output["MS1"] = pd.concat(all_file_ms1, ignore_index=True)
    all_file_ms2 = [file_data['MS2'] for file_data in all_file_data.values() if 'MS2' in file_data]
    all_file_data_output["MS2"] = pd.concat(all_file_ms2, ignore_index=True)
    if verbosity > 0:
        if len(files) >= 2:
            pb.close()
        time_total = round(time.time() - start_time, 2)
        print("Total time:", time_total, "seconds")
    return all_file_data_output

def timeReport(last_time, text):
    current_time = time.time()
    elapsed_time = current_time - last_time
    print(f"{text} - Elapsed time: {timedelta(seconds=elapsed_time)}")
    return current_time
