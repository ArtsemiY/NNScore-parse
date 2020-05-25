============Description============

"NNScore-parse.py" is a script which launch NNScore2.py script step by step 
on all the provided files of ligands and one common file of a receptor.

Script could be launched on both Windows and Linux.
Tested under Windows 10 and Ubuntu 18.04.

Requirements:  
(1) Python3.x
(2) Script needs following python3 packages: 
- tabulate
- pandas
- numpy
- Path
- tqdm
- subprocess.run
(3) AutoDock Vina 1.1.2.

(c) 2020 Artsemi M. Yushkevich, Alexander M. Andrianov. Drug Design Group, The United Institute of Informatics Problem.

============Brief Preparation Manual============

0. Place NNScore2.0 script in the same directory with this script.

1. Install necessary python packages 
For example, using pip (should be installed) by next command for command line: 
pip install tabulate pandas numpy Path tqdm subprocess.run

2. Place set of ligands into separate directory.

3. Run the script "NNScore2_parser.py" from it's directory in cmd by next command:
<path_to_python> NNScore2_parser.py --receptor_file <path_to_receptor> --ligands_dir <path_to_directory_with_ligands> --vina_executable <path_to_vina> --results_file <results_filename>.txt

<path_to_python> - cmd-variable or path to python executable (.exe)
<path_to_directory_with_ligands> - path to separate directory containing ONLY ligands of interest
<path_to_receptor> - name of file in current directory or path to file with receptor (.pdbqt)
<path_to_vina> - cmd-variable or path to vina executable (.exe) [optinal if it defined in NNScore2.py script]
<results_filename>.txt - name of file in which results will be writed [optional, by default == 'results.txt']

If vina(.exe), receptor(.pdbqt) and ligands (directory) placed in same directory as script NNScore2_parser.py, here is examples of such launching:

Example for Windows:
python NNScore2_parser.py --receptor_file receptor.pdbqt --ligands_dir .\ligands\ --vina_executable vina.exe --results_file RES_WINDOWS.txt

Example for Linux:
python NNScore2_parser.py --receptor_file receptor.pdbqt --ligands_dir ./ligands/ --vina_executable vina --results_file RES_LINUX.txt

