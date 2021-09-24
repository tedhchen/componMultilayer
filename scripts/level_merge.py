import csv, configparser, os
import pandas as pd

def merge_data(config, save = True):
	path = config['data']['data']
	accs = pd.read_csv(os.path.join(path, 'twitter_accounts.csv'), header = 0)
	mains = [f for f in os.listdir(path) if f[0:6] == 'check_']
	for main in mains:
		with open(os.path.join(path, main), 'r', encoding = 'utf-8') as infile:
			maindat = pd.read_csv(infile, header = None)
			maindat = maindat[maindat[3] > 0]
			maindat[3].replace({1:2, 2: 3}, inplace = True)
			maindat['org'] = accs[accs['username'] == main[6:-4]].org.item()
			maindat.rename(columns = {0: 'username', 3: 'level'}, inplace = True)
			accs = pd.concat([accs, maindat[['username', 'org', 'level']]])
	if save:
		accs.to_csv(os.path.join(path, 'twitter_merged.csv'), index = False)
	return accs

# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser()
# params.read('config.ini')

# # Running code
# accs = merge_data(path)
