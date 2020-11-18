# ASMDetector- Discovering API Use and Misuse in Python Projects
The project aims at detecting API use and misuse in Python projects along with the taxonomy of API misuse. The command-line tool identifies API misuses in the given Python code snippet with the use of patterns obtained from API usages extracted from GitHub. We introduced a novel pattern mining algorithm and application of the State Machine concept to the domain of API misuse detection.

ASMDetector: An API Misuse Detector for Python language using State Machine Concept.

ASMDetector is divided into Five main sections:
1. Control Flow Graph generation using pycfg. 
	Executable file: pycfg-0.1 
	Input: Python file
	Output: Control Flow Graph

2. ASM (API State Machine) generation. 
	Executable file: ASM.py
	Input: Control Flow Graph
	Output: API State machine having call and control sequences

	Requires list of unnecessary code lines not relevant to given API: 'filename'+'_rstate.txt'. This is not manditory file but requires 		for better performance.
	Requires Data type dictionary: 'typedict.txt'. This is not compulsary file.

3. pattern generation. 
	Executable file: pattern.py
	Input: List of API State machines
	Output: Frequent API State Machines

4. API misuse detection. 
	Executable file: matching.py
	Input: Frequent API State machines, API usage
	Output: Report of API Misuse and their classification- 'report.txt' or 'Docreport.txt'(for API Document results)

5. Detected Misuse classification. 
	Executable file: matching.py

Along with these five section, we have one command line executable file: ASMDetector.py


ASMDetector Usage:
To run the detector, you have to run main executable file ASMDetector.py with command line arguments. These argument contains mode of operation, source file and destination file. The mode of operations dependents whether you want to provide Training dataset of API usages or examples from API documentation for ASM generation.

Mode of operations:
1. Only generate pattern from usages for developers reference.
$ python ASMDetector.py "/path/to/folder/containing/python_usage/files" "/path/to/destination/folder/to/store/results" -p

2. Detecting misuse in training dataset itself.
$ python ASMDetector.py "/path/to/folder/containing/python_usage/files" "/path/to/destination/folder/to/store/results" -mu

3. Detecting misuse in test usages file using patterns generated from training usages files
$ python ASMDetector.py "/path/to/folder/containing/Training/files" "/path/to/folder/containing/Test/files" -mt

4. Detecting misuse in test usages file against constraints example from API Documentation
$ python ASMDetector.py "/path/to/folder/containing/Document_example/files" "/path/to/folder/containing/Test/files" -md

Installations Required:
(Better to use this tool in Linux enviroment)
Install pycfg from https://pypi.org/project/pycfg/
pycfg requires internal library instllations such as graphviz, pygraphviz and astunparse.



