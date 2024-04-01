# DataSUS EDA Python
A collection of Python notebooks and scripts dedicated to Exploratory Data Analysis (EDA) of healthcare data from DataSUS\

This repository contains a collection of Jupyter Notebooks related to healthcare data analyses focusing on Tuberculosis cases and patient data in Brazil's Centro-Oeste region, along with a specific analysis concerning procedure codes.

### Files Overview
- **Tuberculose A15 Janeiro 2023 EDA** (tuberculose_012023.ipynb)\
This notebook provides an Exploratory Data Analysis (EDA) on Tuberculosis cases for January 2023. It includes data cleaning, merging dataframes for different states, replacing NaN values, and creating visualizations to understand the distribution and frequency of Tuberculosis cases across different states. The notebook also outlines steps to save processed data for further analysis or BI visualization tools.

- **Região Centro Oeste PA Janeiro de 2023** (regiao_centro_oeste.ipynb)\
Focusing on the Centro-Oeste region of Brazil, this notebook merges patient data across four states, emphasizing the primary diagnosis code (PA_CIDPRI). It offers insights into the frequency of specific diagnosis codes, provides a pie chart visualization for the N180 code, calculates the weighted average age for each state, and exports the consolidated data to a CSV file for further examination.

- **Converting all the PA Codes** (código_pa.ipynb)\
This notebook is dedicated to processing and converting procedure codes (PA Codes). It includes steps for reading the original data files, ensuring they are in the correct format, and replacing the procedure codes with their descriptions. The process aims to make the dataset more accessible and understandable for users not familiar with the raw codes.

### How to Use
Ensure you have Jupyter Notebook or JupyterLab installed to run these notebooks.\
Each notebook contains step-by-step instructions for data processing and analysis.\
Data files required for analysis are mentioned within the notebooks. Ensure you have access to these files before running the notebooks.\

**Requirements**
- Python 3.x
- Pandas
- Matplotlib (for visualizations)
- Other specific Python packages as mentioned within the notebooks.
