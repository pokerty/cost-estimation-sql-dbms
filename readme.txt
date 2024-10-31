Installation Instruction

1) Download Python version 3.12 and above.
2) Install the requirements in the requirements.txt file by running the command: pip install -r requirements.txt

3) Download Graphviz from the following link (the latest version is graphviz-10.0.1): https://graphviz.org/download/

4) Note: If you are using Windows, You must add the Graphviz bin folder to your PATH environment variable so that your system can find the Graphviz executables.
   4a)Open the Start menu and search for "Environment Variables". 
   4b)Click on the "Edit the system environment variables" option that appears.
   4c)In the System Properties window that appears, click on the "Environment Variables" button.
   4d)In the Environment Variables window, scroll down to the "System Variables" section and find the "Path" variable. Click on the "Edit" button.
   4e) In the Edit Environment Variable window, click on the "New" button and enter the path to the Graphviz bin folder. E.g. "C:\Program Files (x86)\Graphviz2.38\bin" (depending on your Graphviz version and installation location).
   4f) Click "OK" on all windows to close them and save your changes.
   4g) Once you have added the Graphviz bin folder to your PATH environment variable, restart your Windows PC. The changes will be made and you should be able to run Graphviz from the command line or from within your Python code.

5) Run the project.py file to start the program.
