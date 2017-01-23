'''

Pre-process galaxy/random catalogs for P(k) calculation  

Author: ChangHoon Hahn 

'''
import numpy as np 
import pickle 

from ChangTools.fitstables import mrdfits 
import util as UT 


class CatalogInventory(object): 
    ''' Object that keeps inventory of the dictionaries that specify different catalogs, 
    which is saved in a pickle file within the directory. 
    '''
    def __init__(self): 
        self.inventory_dir = UT.code_dir()+'catalog_inventory/'

    def LoadCatalog(self, name, version): 
        ''' Load catalog dictionary given name and version 
        '''
        # load catalog information specified in inventory file
        file_info = ''.join([self.inventory_dir, name, '__', version]) 
        f_info = open(file_info, 'r') 
    
        catalog_info = {} 
        for line in f_info: 
            if line[0] == '#' or line.strip() == '':
                continue
            catalog_info[line.split('=')[0].strip()] = line.split('=')[1].strip()
        
        for key in catalog_info.keys(): 
            if 'column' in key: 
                catalog_info[key] = catalog_info[key].split(',') 
            if key == 'fftflags':
                catalog_info[key] = catalog_info[key].split(',') 
            if key == 'powerflags':
                catalog_info[key] = catalog_info[key].split(',') 
        
        if name != catalog_info['name']: 
            raise ValueError("names do not match") 
        if version != catalog_info['version']: 
            raise ValueError("versions do not match") 

        return catalog_info 

"""
    info_list = pickle.load(open(self.file_inventory, 'rb'))

    for it in info_list: 
        if it['name'] == name and it['version'] == version: 
            catalog_info = it 
    try:  
        return catalog_info  
    except NameError: 
        raise NameError("could not find specified catalog dictionary") 
        
    def AddCatalog(self, catalog_info):  
        ''' Add dictionary to catalog 
        '''
        # check that the catalog information is complete 
        self._Check_Info(catalog_info) 

        # load list of catalog_info dictionaries 
        info_list = pickle.load(open(self.file_inventory, 'rb'))

        # check that the dictionary doesn't already exist 
        for it in info_list: 
            if it == catalog_info: 
                print 'Already in list' 
                return None
            
            if it['name'] == catalog_info['name'] and it['version'] == catalog_info['version']: 
                raise ValueError("conflicting dictionary. Use UpdateCatalog() if you want \
                        to update an existing catalog dictionary") 
        
        info_list.append(catalog_info) 

        pickle.dump(info_list, open(self.file_inventory, 'wb'))
        return None

    def UpdateCatalog(self, catalog_info): 
        ''' Update existing catalog dictionary
        '''
        # check that the catalog information is complete 
        self._Check_Info(catalog_info) 

        # load list of catalog_info dictionaries 
        info_list = pickle.load(open(self.file_inventory, 'rb'))

        # check that the dictionary doesn't already exist 
        for i_it, it in enumerate(info_list): 
            if it == catalog_info: 
                print 'Identifcal to item already in list' 
                return None
            if it['name'] == catalog_info['name'] and it['version'] == catalog_info['version']: 
                i_update = i_it 

        info_list[i_update] = catalog_info.copy() # update the dictionary 
        pickle.dump(info_list, open(self.file_inventory, 'wb'))
        return None

    def _Check_Info(self, catalog_info):  
        ''' check that the catalog information is complete 
        '''
        for key in ['name', 'version', 'dir']: 
            if key not in catalog_info.keys(): 
                raise ValueError("catalog_info dictionary must specify 'name', 'version', 'dir'") 
"""  

def PreProcess(name, version): 
    ''' PreProcess disparate data files in order to general some consistent 
    data file convenient for the fortran files to read in

    notes
    -----
    * this code is messy because of all the different ways people distribute 
        catalogs. I have not figured out a dignified way to do this...
    '''
    CI = CatalogInventory()
    catalog_info = CI.LoadCatalog(name, version)

    for type in ['data', 'ran']: 
        if name == 'eBOSS_QSO': # eBOSS QSO catalogs
            if version == 'v1.6_N': # version 1.6 North 
                # this particular catalog is for the P(k) comparison tests of 
                # https://trac.sdss.org/wiki/eBOSS/QGC/pk_comparison
                file = ''.join([catalog_info['dir_data'], catalog_info['unprocessed_'+type+'_file']]) 
                
                data_fits = mrdfits(file) # data from .fits file ... ugh 
                
                cuts = np.where((data_fits.z > np.float(catalog_info['z_min'])) & 
                        (data_fits.z < np.float(catalog_info['z_max'])))
                print 'impose redshift limit ', catalog_info['z_min'], ' < z < ', catalog_info['z_max']
                print 1.-np.float(len(cuts[0]))/np.float(len(data_fits.z)), ' of galaxies removed in preprocessing'

                # of the many data columns extract: ra, dec, z, n(z), wfkp, wsys, wnoz, wcp
                columns = catalog_info['unprocessed_'+type+'_column']
                
                data_list, data_fmt = [], []  # list of all the data, and list of data formats
                for col in columns:
                    data_list.append(getattr(data_fits, col)[cuts]) 
                    if col == 'nz': 
                        fmt = '%.5e'
                    else: 
                        fmt = '%10.5f'
                    data_fmt.append(fmt) 
                data_hdr = 'columns : '+', '.join(columns)

                # output file name 
                if type == 'data': # galaxy catalog 
                    file_out = ''.join([catalog_info['dir_data'], catalog_info['file'], '.dat']) 
                elif type == 'ran': # random catalog
                    file_out = ''.join([catalog_info['dir_data'], catalog_info['file'], '.ran']) 
        else: 
            raise NotImplementedError
    
        np.savetxt(file_out, 
                (np.vstack(np.array(data_list))).T, 
                fmt=data_fmt, delimiter='\t', header=data_hdr) 
    return None      


if __name__=="__main__": 
    #CI = CatalogInventory()
    #CI.LoadCatalog('eBOSS_QSO', 'v1.6_N') 

    PreProcess('eBOSS_QSO', 'v1.6_N')
