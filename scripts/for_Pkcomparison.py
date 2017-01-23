'''

scratch pad to make code for P(k) comparison 


'''
import numpy as np 
import pk as PK


def makeOutput(name, version): 
    ''' Make P(k) output file in the desired format of the
    https://trac.sdss.org/wiki/eBOSS/QGC/pk_comparison comparison 

    k_mean, k_eff, P0-Pnoise, P2, number_of_modes
    '''
    peek = PK.Pk('eBOSS_QSO', 'v1.6_N')
    peek.Read()
    peek._Rebin_k(np.arange(0.005, 0.41, 0.01)) 

    output_list = [peek.k_mid, peek.k, peek.p0k, peek.p2k, peek.count]

    output_file = ''.join(['/mount/riachuelo1/hahn/power/BigMD/',
        'Pk_eBOSS_QSO_v1.6_forcomparison']) 
    output_fmt = ['%10.5f' for it in output_list]

    np.savetxt(output_file, 
            (np.vstack(np.array(output_list))).T, 
            fmt=output_fmt, delimiter='\t') 
    return None 


if __name__=='__main__': 
    makeOutput('eBOSS_QSO', 'v1.6_N')
