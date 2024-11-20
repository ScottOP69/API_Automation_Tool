import os
import subprocess
import configparser
import shutil


def compare():

    # Config
    config = configparser.ConfigParser()
    config.read('<Give path for Config.ini>')

    # Config Paths

    sybase_dir = '' # Sybase response folder
    sql_dri = '' # sql response folder
    output_dir_report= '' # output dir for comparison reports
    output_dir_summary= '' # output dir for summary reports
    script_path_report = '' # CLI .txt file, for BC to run
    script_path_summary = ''  # CLI .txt file, for BC to run


    # Paths for copying the reports to the LAN location

    source_folder = ''
    destination_folder = ''

    os.makedirs(output_dir_report,exist_ok=True)

    # Function to extract the base Name
    def get_base_name(fileName,suffix):
        if fileName.endswith(suffix):
            return fileName[:-len(suffix)]
        return None

    # List Sybase and SQL Files
    sybase_files = [f for f in os.listdir(sybase_dir) if f.endswith(".xlsx")]
    sql_files = [f for f in os.listdir(sql_dri) if f.endswith(".xlsx")]

    # Generate BC script to generate Comparison report
    with open(script_path_report,'w') as script_file :
        for i, j in zip(sybase_files,sql_files):
            report_name = "_".join(i.split('_')[:2])
            report_name = report_name.split('.')[0]
            report_file = os.path.join(output_dir_report,f"{report_name}.html")

            # Write the file-report command
            report_command =(
                f'file-report layout:side-by-side options:display-all &\n'
                f'output-to:"{report_file}" output-options:wrap-word,thml-color'
                f'{sybase_dir}/{i} {sql_dri}/{j}'
            )

            script_file.write(report_command + '\n')

    # Generate BC script to generate summary reports

    with open(script_path_summary, 'w') as script_file:
        for i, j in zip(sybase_files, sql_files):
            report_name = "_".join(i.split('_')[:2])
            report_name = report_name.split('.')[0]
            report_file = os.path.join(output_dir_report, f"{report_name}.html")

            # Write the file-report command
            report_command = (
                f'file-report layout:summary options:display-all &\n'
                f'output-to:"{report_file}" output-options:wrap-word,thml-color'
                f'{sybase_dir}/{i} {sql_dri}/{j}'
            )

            script_file.write(report_command + '\n')


    # Execute the Script using BC
    subprocess.run(['bcompare.exe', f'@{script_path_report}'], check=True)
    subprocess.run(['bcompare.exe', f'@{script_path_summary}'], check=True)

    # Copy all the files to the Lan location
    copy_files(source_folder, destination_folder)
    print("---------------------------------------------------")
    print("Responses have been captured using Beyond Compare tool")

def copy_files(source_folder, destination_folder):

    # Ensure that the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Loop through all the files in the source folder
    for file_name in os.listdir(source_folder):

        # Full path for the source file
        source_file = os.path.join(source_folder,file_name)

        # Full path for the destination file
        destination_file = os.path.join(destination_folder,file_name)

        # Copt the files
        shutil.copy(source_file,destination_file)

    print("Comparison reports have been generated")

