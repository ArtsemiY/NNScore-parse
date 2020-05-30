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
import shutil
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
	parser.add_argument('--num_to_filter', required=True,
    	help='''number of compounds to take in final set''')
	parser.add_argument('--nn2_script',
    	help='''path to NNScore2 script file''')
	parser.add_argument('--results_file',
    	help='''path to file with results of NNScore work''')
	parser.add_argument('--best_output_dir',
		help='''path to directory with best results in PDBQT format''')
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
	
	#check, whether results_file path defined: if so, set user-defined path, otherwise set results_file 'results.txt' in a local directory
	if not enter.results_file:
		results_text_file = str(script_dir / 'NNScore_results.txt') 
	else:
		results_text_file = enter.results_file
	
	#check, whether best_output_dir path defined: if so, set user-defined path, otherwise set directory 'NNScore_best_N' in a local directory
	if not enter.best_output_dir:
		best_output_directory = str(script_dir) + os.sep + 'NNScore_top-' + str(enter.num_to_filter) + os.sep
	else:
		best_output_directory = enter.best_output_dir

	if os.path.exists(best_output_directory):
		shutil.rmtree(best_output_directory)
	os.mkdir(best_output_directory)

	best_results_text_file = str(script_dir) + os.sep + 'NNScore_best_' + str(int(enter.num_to_filter)) + '_results.txt'
	
	#make temporary directory for NNScore results
	temp_dir = str(script_dir / 'temp') + os.sep
	if os.path.exists(temp_dir):
		shutil.rmtree(temp_dir)
	os.mkdir(temp_dir)

	print("NNScore launch...")
	for ligand_file in tqdm(glob.glob(enter.ligands_dir + "*.pdbqt")):
		ligand_filename = Path(ligand_file).stem
		out_file = open(temp_dir + ligand_filename + ".txt", 'w');
		subprocess.call([sys.executable, nn2_script_file, "-receptor", str(enter.receptor_file), "-ligand", ligand_file, "-vina_executable", str(enter.vina_executable)], stdout=out_file)
		out_file.close()

	print("Collecting results...")
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
					"Kd": float(tmp[4][:-3]),
					"Unit": str(tmp[4][-2:]) 	  
					}
					results_list.append(ligand_dock_info)

	#remove temporary directory of NNScore results
	shutil.rmtree(temp_dir)
    
	print("Sorting results by Kd...")
	results_df = pd.DataFrame(results_list)
	#sorting dataframe with results by score
	results_df.sort_values(by=["NNScore"], ascending=False, inplace=True)

    #placing columns in desirable order
	results_df = results_df[['Filename of ligand', 'NNScore', '\u00B1Deviation', 'Kd', 'Unit']]
	
	# create file with results
	content = tabulate(results_df.values.tolist(), list(results_df.columns), tablefmt="plain")
	open(results_text_file, "w").write(content)
	
	print("Creating directory with top-" + str(int(enter.num_to_filter)) + " results by Kd...")
	results_df_best = results_df.head(int(enter.num_to_filter))
	
	chosen_results = results_df_best['Filename of ligand'].tolist()
	for ligand_file in tqdm(glob.glob(enter.ligands_dir + "*.pdbqt")):
		ligand_filename = Path(ligand_file).stem
		if ligand_filename in chosen_results:
			ligand_file_from = ligand_file
			ligand_file_to = best_output_directory + ligand_filename + '.pdbqt'
			shutil.copy(str(ligand_file_from), str(ligand_file_to))
	
	# create file with best results
	content2 = tabulate(results_df_best.values.tolist(), list(results_df_best.columns), tablefmt="plain")
	open(best_results_text_file, "w").write(content2)

	print("Best " + str(int(enter.num_to_filter)) + " results directory: " + best_output_directory)
	print("Program terminated successfully! ^_^")

if __name__=="__main__": main()
