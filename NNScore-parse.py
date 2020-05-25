"""NNScore-parse is software aimed to make multiligand 
run of NNScore2.0 script.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

NNScore-parse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright 2020 Artsemi M. Yushkevich, Alexander M. Andrianov. Drug Design Group, The United Institute of Informatics Problem.
If you have any questions, comments, or suggestions, please don't hesitate to contact me at fpm.yushkeviAM [at] bsu [dot] by.
"""
import os
import sys
import argparse
import glob
import subprocess
import pandas as pd
import numpy as np

from pathlib import Path
from tabulate import tabulate
from tqdm import tqdm

script_dir = Path(__file__).resolve().parent

def createParser():
	"""
	Create parser for cmd arguments
	
	"""
	parser = argparse.ArgumentParser( 
		description='''This script make multiligand run of NNScore 2.0.''', 
		epilog='''(c) 2020 Artsemi M. Yushkevich, Alexander M. Andrianov. Drug Design Group, The United Institute of Informatics Problem.''')
	parser.add_argument('--receptor_file', required=True,
    	help='''path to receptor file in PDBQT format.''')
	parser.add_argument('--ligands_dir', required=True,
    	help='''path to separate directory with ligands in PDBQT format''')
	parser.add_argument('--vina_executable', required=True,
    	help='''path to vina executable file''')
	parser.add_argument('--nn2_script',
    	help='''path to NNScore2 script file''')
	parser.add_argument('--results_file',
    	help='''path to file with results of NNScore work''')
	return parser


def main():
	"""
	Run the program
	
	Arguments:
	args -- an array containing the system parameters. sys.argv format.

	"""
	
	args = createParser()
	enter = args.parse_args()
	
	#check, whether nn2_script path defined: if so, set user-defined path, otherwise set NNScore2 script from a local directory of this script
	if not enter.nn2_script:
		nn2_script_file = str(script_dir / 'NNScore2.py')
	else:
		nn2_script_file = enter.nn2_script
	
	#check, whether output_dir path defined: if so, set user-defined path, otherwise set directory 'output' in a local directory
	if not enter.results_file:
		results_text_file = str(script_dir / 'results.txt') 
	else:
		results_text_file = enter.results_file
	
	#make temporary directory
	temp_dir = str(script_dir / 'temp') + os.sep
	if not os.path.exists(temp_dir):
		os.mkdir(temp_dir)
	else:
		for file in glob.glob(temp_dir + "*.*"):
			os.remove(file)

	print("NNScore launch...")
	for ligand_file in tqdm(glob.glob(enter.ligands_dir + "*.pdbqt")):
		ligand_filename = Path(ligand_file).stem
		#os.system(to_execute)
		temp_out_file = open(temp_dir + ligand_filename + ".txt", 'w');
		subprocess.call([sys.executable, nn2_script_file, "-receptor", str(enter.receptor_file), "-ligand", ligand_file, "-vina_executable", str(enter.vina_executable)], stdout=temp_out_file)
		temp_out_file.close()

	print("Writing results...")
	results_list = []
	for ligand_output in tqdm(glob.glob(temp_dir + "*.txt")):
		with open(ligand_output,'r') as f:
			while True:
				line = f.readline()
				if len(line) == 0: break
				if "AVERAGE SCORE OF ALL 20 NETWORKS, BY POSE" in line:
					line = f.readline()
					line = f.readline()
					line = f.readline()
					tmp = line.replace(' ', '')
					tmp = tmp.replace('\n', '')
					tmp = tmp.split('|')
					
					ligand_dock_info = {
					"Filename of ligand": str(Path(ligand_output).stem),
					"NNScore": float(tmp[2]),
					"\u00B1Deviation": float(tmp[3]),
					"Energy": float(tmp[4][:-3]),
					"Unit": str(tmp[4][-2:]) 	  
					}
					results_list.append(ligand_dock_info)
	
	for file in glob.glob(temp_dir + "*.*"):
		os.remove(file)
	os.rmdir(temp_dir)
        
	results_df = pd.DataFrame(results_list)
	#sorting dataframe with results by score
	results_df.sort_values(by=["NNScore"], ascending=False, inplace=True)

        #placing columns in desirable order
	results_df = results_df[['Filename of ligand', 'NNScore', '\u00B1Deviation', 'Energy', 'Unit']]
	
	# create file with results
	content = tabulate(results_df.values.tolist(), list(results_df.columns), tablefmt="plain")
	open(results_text_file, "w").write(content)
	print(content)
	
	print("Program terminated successfully! ^_^")

if __name__=="__main__": main()
