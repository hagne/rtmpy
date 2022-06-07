import struct
import pandas as pd
import numpy as np



######
def read_tape12_file(path2file):
#     fn = './lblrtm_example_files/TAPE12'

    def read_file_header(file_buffer, byte_oder = '<', precision = 'single'):
        header_eft = byte_oder
        header_eft +='i'*266
        # header_eft +='i'*356
        est_header = struct.calcsize(header_eft)
        header_record = file_buffer.read(est_header)
        print(est_header)
        file_header = struct.unpack(header_eft,header_record)
        return file_header
    
    def read_panel(file_buffer, byte_oder = '<', precision = 'single'):
    #### block header
        block_header_eft = byte_oder
        block_header_eft +='iddfiii'
        block_header_est = struct.calcsize(block_header_eft)
        block_header_record = file_buffer.read(block_header_est)
        block_header_values = struct.unpack(block_header_eft, block_header_record)
        _,v_start, v_end, v_spacing, npts,_, lentest= block_header_values
        assert(_==24), f'is {_}, soll 24'
        assert(4*npts == lentest), f'lentest: {lentest}, problem with internal file inconsistency'
        data_eft = byte_oder + (npts * 'f')
        record = file_buffer.read(struct.calcsize(data_eft))
        radiance = struct.unpack(data_eft,record)
        lentest_2 = struct.unpack('i',file_buffer.read(4))[0]
        assert(lentest == lentest_2), f'lentest_2: {lentest_2}, problem with internal file inconsistency'
        lentest_3 = struct.unpack('i',file_buffer.read(4))[0]
        assert(lentest == lentest_3), f'lentest_3: {lentest_3}, problem with internal file inconsistency'
        record = file_buffer.read(struct.calcsize(data_eft))
        trans = struct.unpack(data_eft,record)
        lentest_4 = struct.unpack('i',file_buffer.read(4))[0]
        assert(lentest == lentest_4), f'lentest_4: {lentest_4}, problem with internal file inconsistency'
        df = pd.DataFrame({'radiance':radiance, 'transmissivity': trans}, index = np.linspace(v_start, v_end, npts))
        out = {'data': df}
        return out
    
    data = pd.DataFrame()
    with open(path2file, mode='rb') as rein:
        file_header = read_file_header(rein)
        thereismore = True
        while thereismore:
            out = read_panel(rein)
            dft = out['data']
            data = pd.concat([data,dft])
            if dft.shape[0] < 2400:
                thereismore = False

    data.index.name = 'wavennumber (cm-1)'
    return data

def read_tape27_file(path2file):
    fn = path2file
    # pd.read_csv(fn, skiprows=25)
    df = pd.read_fwf(fn, skiprows=25)
    df.index = 1/(df.WAVENUMBER) *1e7
    df.drop('0', axis = 1, inplace=True)
    df.drop('WAVENUMBER', axis = 1, inplace=True)
    return df