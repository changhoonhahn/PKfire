'''

Utility functions for Central Quenching project 

Author(s): ChangHoon Hahn

'''
import os 
import os.path

import subprocess


def code_dir(): 
    return os.path.dirname(os.path.realpath(__file__))+'/'


class FORTcode: 
    def __init__(self, FORTfile): 
        ''' Class to describe FORTRAN code for powerspectrum calculations 

        parameters
        ----------
        FORTfile : fortran file 
        '''
        self.dir = code_dir()+'fortran/' # fortran code directory
        self.FORTfile = FORTfile # fortran code 

        self.code = ''.join([self.dir, FORTfile])
        self.exe = self.fexe()  

    def fexe(self): 
        ''' Fortran executable that corresponds to fortran code
        '''
        code_dir = ''.join(['/'.join((self.code).split('/')[:-1]), '/'])
        code_file = (self.code).split('/')[-1]
    
        fort_exe = ''.join([code_dir, 'exe/', '.'.join(code_file.rsplit('.')[:-1]), '.exe'])
        self.exe = fort_exe 
        
        return fort_exe 

    def Compile(self):
        ''' Compile fortran code
        '''
        # compile command for fortran code. Quadruple codes have more
        # complex compile commands specified by Roman 
        if self.FORTfile == 'FFT_fkp_quad.f': 
            compile_cmd = ' '.join([
                'ifort -fast -o', 
                self.exe, 
                self.code, 
                '-L/usr/local/fftw_intel_s/lib -lsrfftw -lsfftw -lm'
                ])
        elif self.FORTfile == 'power_quad.f': 
            compile_cmd = ' '.join([
                'ifort -fast -o', 
                self.exe, 
                self.code
                ])
        else: 
            compile_cmd = ' '.join([
                'ifort -O3 -o', 
                self.exe, 
                self.code, 
                '-L/usr/local/fftw_intel_s/lib -lsfftw -lsfftw'
                ])

        print ' ' 
        print 'Compiling ------'
        print compile_cmd
        print '----------------'
        print ' ' 

        # call compile command 
        subprocess.call(compile_cmd.split())
        return None 

    def tMod(self): 
        ''' Return the times the .f and .exe files were last modified 
        '''
        if not os.path.isfile(self.code): 
            fcode_t_mod = 0 
        else: 
            fcode_t_mod = os.path.getmtime(self.code)

        if not os.path.isfile(self.exe): 
            fexe_t_mod = 0 
        else: 
            fexe_t_mod = os.path.getmtime(self.exe)
        return [fcode_t_mod, fexe_t_mod]
