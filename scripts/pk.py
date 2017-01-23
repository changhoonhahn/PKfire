'''

Use the FFT files to finally calculate P(k) 

'''
import numpy as np 
import os 
import subprocess

import util as UT 
import catalog as Cat

class Pk(object): 

    def __init__(self, name, version): 
        ''' Powerspectrum class object
        '''
        self.name = name # name of survey/simulation 
        self.version = version # specific version 
        
        # load all the run information via CatalogInventory 
        CI = Cat.CatalogInventory()
        self.catalog_info = CI.LoadCatalog(self.name, self.version)
        self._Check_CatInfo() 

    def File(self): 
        file_pk = ''.join([self.catalog_info['dir_power'], 
            'Pk_', # FFT 
            self.catalog_info['name'], '.', self.catalog_info['version'], #self.catalog_info['file'], # specify survey name and version 
            self._Flags() # specify the important fft and P(k) flags 
            ])
        return file_pk 

    def Read(self): 
        ''' Read in constructed P(k) file. 
        '''
        if self.catalog_info['power_code'] == 'power_quad.f': 
            self.data_cols = ['k', 'p0k', 'p2k', 'p4k', 'count']
            col_index = [0, 1, 2, 3, -2]

        pk_data = np.loadtxt(
                    self.File(), 
                    unpack = True, 
                    usecols = col_index)
        
        for i_col, col in enumerate(self.data_cols): 
            setattr(self, col, pk_data[i_col])
        return None
     
    def _Rebin_k(self, k_bins): 
        ''' Rebin P(k) to specified k_bins 
        '''
        kavg = np.zeros(len(k_bins)-1) 
        new_datacols = [np.zeros(len(k_bins)-1) for col in self.data_cols]
        for i_k in range(len(k_bins)-1): 
            # k bin range 
            k_lim = np.where((self.k >= k_bins[i_k]) & (self.k < k_bins[i_k+1])) 
            if len(k_lim) == 0: 
                continue 

            kavg[i_k] = np.sum(self.k[k_lim] * self.count[k_lim]) / np.sum(self.count[k_lim]) 
            
            for i_col, col in enumerate(self.data_cols): 
                if col != 'count': 
                    (new_datacols[i_col])[i_k] = np.sum(getattr(self, col)[k_lim] * self.count[k_lim]) / np.sum(self.count[k_lim]) 
                else: 
                    (new_datacols[i_col])[i_k] = np.sum(self.count[k_lim]) 
        self.k = kavg
        self.k_mid = 0.5 * (k_bins[:-1] + k_bins[1:]) 
        for i_col, col in enumerate(self.data_cols): 
            setattr(self, col, new_datacols[i_col]) 
        #self.k_eff = kavg # average of the k-modes

        return None 

    def Construct(self, clobber=False):
        ''' Calculate P(k) from FFTs of galaxy data catalog and random catalogs.
        '''
        # check that both the data and random FFT files exist. 
        #fft_file = lambda dorr: ''.join([self.catalog_info['dir_fft'], 
        #    'FFT_', self.catalog_info['file'], '.', dorr, FFT.FFT_flags(self.catalog_info)])
        #print fft_file('dat')
        #print fft_file('ran')
        if any([not os.path.isfile(self._FFT_file(0)), clobber]): # run FFT files otherwise
            self.RunFFT(DorR=0) 
        if not os.path.isfile(self._FFT_file(1)): 
            self.RunFFT(DorR=1) 

        # import fortran code object for P(k) code
        fort = UT.FORTcode(self.catalog_info['power_code']) 
        fcode_t_mod, fexe_t_mod = fort.tMod() 
        if fcode_t_mod > fexe_t_mod: 
            # if code was more recently modified than the exe 
            # then compile it 
            print 'Compiling P(k) code'
            fort.Compile() 
        
        # construct commandline call
        cmd_list = [fort.exe] 
        # data fft
        cmd_list.append(self._FFT_file(0))
        # random fft
        cmd_list.append(self._FFT_file(1))
        # P(k) file 
        file_pk = self.File() 
        cmd_list.append(file_pk)
        
        for i_flag in range(len(self.catalog_info['powerflags'])): 
            cmd_list.append(self.catalog_info['power_flag'+str(i_flag)])

        cmdline_call = ' '.join(cmd_list) 
        
        # run the code using subprocess 
        print ''
        print '-----------------------'
        print 'Constructing '
        print file_pk  
        print '-----------------------'
        print ''
        print cmdline_call 
        print '-----------------------'

        subprocess.call(cmdline_call.split())
        return None 

    def RunFFT(self, DorR=0, clobber=False): 
        ''' Calculate FFT. This is essentially a python wrapper for 
        FORTRAN fft codes in fortran/.

        DorR : int 
            if DorR = 0, run mock 
            if DorR = 1, run random 
        '''
        # import fortran code object
        fort = UT.FORTcode(self.catalog_info['fft_code']) 
        fcode_t_mod, fexe_t_mod = fort.tMod() 
        if fcode_t_mod > fexe_t_mod: 
            # if code was more recently modified than the exe 
            # then compile it 
            print fcode_t_mod, fexe_t_mod
            fort.Compile() 
        
        # construct command line call for FFT fortran 
        cmd_list = [fort.exe] 
        for i_flag in range(len(self.catalog_info['fftflags'])): 
            cmd_list.append(self.catalog_info['fft_flag'+str(i_flag)])

        # data or random 
        if DorR == 0: 
            file_ext = 'dat'
        else: 
            file_ext = 'ran' 
        cmd_list.append(str(DorR)) 

        # data file (specified by Cat.PreProcess) 
        file_data = ''.join([self.catalog_info['dir_data'], self.catalog_info['file'], '.', file_ext])
        cmd_list.append(file_data) # append data file 
        if not os.path.isfile(file_data): 
            raise ValueError("The data file, "+file_data+" does not exist.\
                    Run through Cat.PreProcess to construct it.")
    
        file_fft = self._FFT_file(DorR)
        if os.path.isfile(file_fft) and clobber: 
            if DorR == 1: 
                print 'Random FFT already exists. This calculation takes a while, \
                        so if you want to run it again, manually delete the FFT file \
                        to illustrate your commitment'
                return None 
        # append fft file
        cmd_list.append(file_fft) 

        cmdline_call = ' '.join(cmd_list) 
        
        # run the code using subprocess 
        print ''
        print '-----------------------'
        print 'Constructing '
        print file_fft  
        print '-----------------------'
        print ''
        print cmdline_call 
        print '-----------------------'

        subprocess.call(cmdline_call.split())

        return None 

    def _FFT_file(self, DorR): 
        ''' Get FFT file name of either data (DorR = 0) or random (DorR = 1) FFT. 
        '''
        if DorR == 0: 
            file_ext = 'dat'
        else: 
            file_ext = 'ran' 
        # fft file (which specifies the main choices)
        file_fft = ''.join([self.catalog_info['dir_fft'], 
            'FFT_', # FFT 
            self.catalog_info['name'], '.', self.catalog_info['version'], #self.catalog_info['file'], # specify survey name and version 
            '.', file_ext, # random or data 
            self._FFT_flags() # specify the important fft flags 
            ])
        return file_fft

    def _Flags(self): 
        ''' From catalog_info dictionary construct a string that specifies the 
        important choices in FFT and P(k) calculation.
        '''
        fft_flags = self.catalog_info['fftflags'] # list of FFT file flags

        # determine flag specifing strings  
        flag_specs = [] 
        for i_flag in range(len(fft_flags)): 
            if fft_flags[i_flag] != '00': 
                if fft_flags[i_flag] == 'cosmology': 
                    if self.catalog_info['fft_flag'+str(i_flag)] == '0': 
                        flag_specs.append('FidCosmo')   # fiducial cosmology
                    else: 
                        flag_specs.append('MockCosmo')  # cosmology of the mock 
                else: 
                    flag_specs.append(fft_flags[i_flag]+self.catalog_info['fft_flag'+str(i_flag)])

        flags = self.catalog_info['powerflags'] # list of power flags
        
        # determine flag specifing strings  
        for i_flag in range(len(flags)): 
            if flags[i_flag] != '00': 
                if flags[i_flag] == 'Lbox': 
                    # Lbox is already specified above 
                    pass
                else: 
                    flag_specs.append(flags[i_flag]+self.catalog_info['power_flag'+str(i_flag)])

        return '.'+'.'.join(flag_specs)

    def _FFT_flags(self): 
        ''' From catalog_info dictionary construct a string that specifies the 
        import choices in the FFT.
        '''
        flags = self.catalog_info['fftflags'] # list of FFT file flags
        
        # determine flag specifing strings  
        flag_specs = [] 
        for i_flag in range(len(flags)): 
            if flags[i_flag] != '00': 
                if flags[i_flag] == 'cosmology': 
                    if self.catalog_info['fft_flag'+str(i_flag)] == '0': 
                        flag_specs.append('FidCosmo')   # fiducial cosmology
                    else: 
                        flag_specs.append('MockCosmo')  # cosmology of the mock 
                else: 
                    flag_specs.append(flags[i_flag]+self.catalog_info['fft_flag'+str(i_flag)])

        return '.'+'.'.join(flag_specs)

    def _Check_CatInfo(self): 
        ''' Some small consistency checks in the catalog info dictionary 
        '''
        fft_flags = self.catalog_info['fftflags'] # list of FFT file flags
        pk_flags = self.catalog_info['powerflags']

        fft_lbox = int(self.catalog_info['fft_flag'+str(fft_flags.index('Lbox'))])
        power_lbox = int(self.catalog_info['power_flag'+str(pk_flags.index('Lbox'))])

        if fft_lbox != power_lbox: 
            raise ValueError("Lbox values do not match between FFT and Power flags!")
        return None 




if __name__=='__main__': 
    peek = Pk('eBOSS_QSO', 'v1.6_N')
    peek.Construct(clobber=False)
