__author__ = 'Vale'

import platform
import os
import json
import subprocess
import re
import tkMessageBox
import tkFileDialog
from tkCommonDialog import Dialog

class propc_library_finder:
    library_path = ""
    
    def __init__( self, *args, **kwargs ):
        self.find_libraries()
        output = self.assemble_information()
        self.create_json_file( output, "lib-descriptor.json" )
    
    def get_directory( self ):
        global library_path
    
        return library_path
    
    def find_libraries( self ):
        global library_path
        
        file_path = self.askdirectory()
    
        library_path = file_path

    def get_subdirectories( self, path ):
        return os.listdir( path )

    def get_files_in_directory( self, path ):
        files = []
        
        for file in os.listdir( path ):
            if isfile( file ):
                files[ file ] = file

        return files
    
    def assemble_information( self ):
        global library_path
        output = "[\n"
    
        #get directories
        directories = self.get_subdirectories( library_path )
        
        for directory in directories:
            directory_path = library_path + "/" + directory + "/"
            
            #get subdirectories of that directory
            try:
                sub_directories = self.get_subdirectories( directory_path )
            
                for sub_directory in sub_directories:
                    if ( "." not in sub_directory ):
                        sub_directory_name = re.sub( "lib", "", sub_directory )
                        sub_directory_path = directory_path + sub_directory
                
                        output += '\t{\n\t\t'
                        output += '"name": "' + sub_directory_name + '",\n\t\t'
                        output += '"libdir": "' + sub_directory_path + '",\n\t\t'
                        output += '"include": [\n\t\t\t' + '"' + sub_directory_name + '"'
                        output += '\n\t\t],\n\t\t'
                        output += '"memorymodel": {\n\t\t\t"cmm": "' + sub_directory_path + '/cmm/"' + '\n\t\t}\n\t},\n'
            except:
                pass
    
        output = output[:len(output) - 2]
        output += '\n]'
        
        return output

    def create_json_file( self, data, file_name ):
        file = open( file_name, 'w' )
        file.write( data )
        file.close()
    
        #json.dump( unicode( data ), file_name )
        print json.load(open(os.getcwd() + "/lib-descriptor.json"))
    
    def askdirectory(self, **options):
        "Ask for a directory name"
        
        return apply(self.Chooser, (), options).show()

    class Chooser(Dialog):
    
        command = "tk_chooseDirectory"
        
        def _fixresult(self, widget, result):
            if result:
                # keep directory until next time
                self.options["initialdir"] = result
            self.directory = result # compatibility
            return result

    #
    # convenience stuff

if __name__ == '__main__':
    tkMessageBox.showinfo( "ERROR", "This program cannot be run as a standalone application" )

    #library_finder_test = propc_library_finder()