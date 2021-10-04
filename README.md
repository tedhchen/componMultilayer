# componMultilayer
Repository for multilayer network approaches to working with climate governance data.

<img src="pipeline.png" alt="Data Collection Pipeline" width="75%"/>

## Contents
- Quick start
- Protocol
- Summary of files

## Quick Start 
\* = teams not running scripts can ignore these steps.
1. \*Clone the repository.
2. \*Install the required packages (see [`compontwitter.yml`](https://github.com/tedhchen/componMultilayer/blob/main/compontwitter.yml)).
3. \*Change [`config.ini.template`](https://github.com/tedhchen/componMultilayer/blob/main/scripts/config.ini.template) into `config.ini` and enter your own settings.
4. Collect the main accounts (steps 01 and 02).
5. \*Run Notebook for step 03. 
6. Label all side accounts (step 04).
7. \*Merge data and voilà!

## Protocol
Details about data collection and labeling for each of the steps outline below can be found in the [`TwitterCodebook.pdf`](https://github.com/tedhchen/componMultilayer/blob/main/TwitterCodebook.pdf).

### 00. Identify roster actors
You should have a predefined list of policy actors. This protocol does not address how to bound policy systems and identify policy actors.

### 01. Identify collective main
In this step, you should find the collective main account of each of your policy actors and provide a list of keyword for filtering the side accounts. Document them in the template file ([`template\main_accounts.csv`](https://github.com/tedhchen/componMultilayer/blob/main/templates/main_accounts.csv)) and assign them with `level` 0. When entering the account names, do not include the @ sign. Make sure this file is encoded in UTF-8.

### 02. Identify individual main
In this step, you should find the individual main accounts of each of your policy actors. Document them in the template file ([`template\main_accounts.csv`](https://github.com/tedhchen/componMultilayer/blob/main/templates/main_accounts.csv)) and assign them with `level` 1. When entering the account names, do not include the @ sign. Make sure this file is encoded in UTF-8.

### 0a. Standardize formatting of main accounts
This step needs to be done before step 05. Doing it as early as possible after steps 01 and 02 will ensure the most consistent data (so accounts do not change their usernames). Run the Jupyter Notebook [`0a_standardize_main.ipynb`](https://github.com/tedhchen/componMultilayer/blob/main/scripts/0a_standardize_mains.ipynb). The output file will be used by a later step, but can be ignored for now.

### 03. Identify side accounts
Only do this step after `main_accounts.csv` has been filled with the collective main accounts and their keywords (step 01). Run the Jupyter Notebook [`03_identify_sides.ipynb`](https://github.com/tedhchen/componMultilayer/blob/main/scripts/03_identify_sides.ipynb). It will create coding sheets for each of your collective main accounts (as long as they have potential side accounts).

### 04. Classify side accounts
Only do this step after step 03 is complete. Go through each of the `check_[org].csv` file and classify the accounts based on instructions in the protocol file. Enter the level of the account in the 4th column and save the file. Collective side accounts are labeled 2, individual side accounts are labeled 3, and unrelated accounts are left blank. If an account should be included as individual main (but was not included in step 02), it is fine to label them in this step as 1.

### 05. Merge all levels
After all preceding steps are complete, run the Jupyter Notebook [`05_levels_merge.ipynb`](https://github.com/tedhchen/componMultilayer/blob/main/scripts/05_levels_merge.ipynb). This will create an output file `all_accounts.csv`, which contains all policy actors' accounts and their levels. We will use this to collect Twitter behavior of our policy actors.

## Summary of files
- `data\`: suggested location for setting up working/scratch space
- `example\`: illustation of the pipeline
    - `main_accounts.csv`: this is the file where main accounts and keywords were manually entered
    - `check_cxaalto.csv` and `check_ecanettutkimus.csv`: files returned by the notebook in step 03. Hand labeled according to step 04.	
	- `main_standardized.csv`: file used for final merging, returned by the notebook in step 0a.
	- `all_accounts.csv`: final product of this data collection exercise. Returned by the notebook in step 05.
- `scripts\`: main directory where the scripts and notebooks are stored
    - `03_identify_sides.ipynb`: notebook for step 03.
	- `0a_standardize_mains.ipynb`: notebook for step 0a.
	- `05_levels_merge.ipynb`: notebook for step 05.
	- `config.ini.template`: remove ".template" and enter Twitter API credentials and data directory (suggested to be `data\` from this repo).
- `templates\`: contains the template for steps 01 and 02.
- `TwitterCodebook.pdf`: detailed outline of data collection and labeling protocol
