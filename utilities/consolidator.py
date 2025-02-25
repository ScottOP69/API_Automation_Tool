import os
from bs4 import BeautifulSoup
import xlsxwriter

# Define paths (update these to match your environment)
folder1_path = 'results/comparison-reports'  # Comparison reports folder
folder2_path = 'results/summary-reports'    # Summary reports folder
output_path = 'results/FinalReport.xlsx'    # Output Excel file

# Extract data from HTML report
def extract_report_data(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        report_data = {}
        
        # Extract file paths
        report_data['left_file'] = soup.text.split('Left file: ')[1].split('&nbsp;')[0].strip()
        report_data['right_file'] = soup.text.split('Right file: ')[1].split('&nbsp;')[0].strip()

        # Extract summary differences
        lines = soup.text.splitlines()
        differences = [line.strip() for line in lines if 'important' in line.lower()]
        report_data['summary'] = "\n".join(differences) if differences else "No differences"

        # Determine if there are important differences
        report_data['difference'] = "Yes" if differences else "No"
        
        return report_data

# Generate Excel report
def generate_excel_report(folder1_path, folder2_path, output_path):
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet()

    # Write headers
    headers = ['File Name', 'Difference', 'Summary', 'Comparison Report Link', 'Summary Report Link']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Add formatting for hyperlinks
    hyperlink_format = workbook.add_format({'color': 'blue', 'underline': 1})

    # Get the list of HTML files in each folder
    comparison_files = sorted([f for f in os.listdir(folder1_path) if f.endswith('.html')])
    summary_files = sorted([f for f in os.listdir(folder2_path) if f.endswith('.html')])

    for idx, (comp_file, summary_file) in enumerate(zip(comparison_files, summary_files), start=1):
        # Extract data from the comparison report
        comp_file_path = os.path.join(folder1_path, comp_file)
        summary_file_path = os.path.join(folder2_path, summary_file)

        report_data = extract_report_data(comp_file_path)

        # Extract file name
        file_name = os.path.basename(report_data['left_file'])

        # Write data to the worksheet
        worksheet.write(idx, 0, file_name)  # File Name
        worksheet.write(idx, 1, report_data['difference'])  # Difference
        worksheet.write(idx, 2, report_data['summary'])  # Summary

        # Insert hyperlinks to the reports
        comp_link = f'file:///{comp_file_path}'
        summary_link = f'file:///{summary_file_path}'
        worksheet.write_url(idx, 3, comp_link, hyperlink_format, 'Open Comparison Report')  # Comparison Report Link
        worksheet.write_url(idx, 4, summary_link, hyperlink_format, 'Open Summary Report')  # Summary Report Link

    # Close workbook
    workbook.close()
    print(f"Report generated successfully at {output_path}")

# Call the function
generate_excel_report(folder1_path, folder2_path, output_path)
