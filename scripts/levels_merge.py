import csv, configparser, os
import pandas as pd

def merge_data(path, save = True):
	df = pd.read_csv(os.path.join(path, 'main_standardized.csv'), dtype = {'id':'str'}, header = 0)
	mains = [f for f in os.listdir(path) if f[0:6] == 'check_']
	for main in mains:
		main_id = main[6:-4]
		maindat = pd.read_csv(os.path.join(path, main), header = None, dtype = {0:'str', 3:'Int64'}, delimiter = ',', encoding = 'utf-8')
		maindat = maindat[maindat[3] > 0]
		if main_id.isnumeric():
			org = df[(df['id'] == main_id) & (df['level'] == 0)].org.item()
		else:
			org = df[(df['sn'] == main_id) & (df['level'] == 0)].org.item()
		maindat['org'] = org
		maindat.rename(columns = {0:'id', 1:'sn', 3:'level'}, inplace = True)
		df = pd.concat([df, maindat[['org', 'id', 'sn', 'level']]])
	df.sort_values(by = ['org', 'level', 'id'], axis = 0, inplace = True)
	df.drop_duplicates(subset = ['org', 'id'], inplace = True)	
	if save:
		df.to_csv(os.path.join(path, 'all_accounts.csv'), sep = ',', index = False)
	return df

# # Example code, uncomment to run:
# # Reading in configuation
# params = configparser.ConfigParser()
# params.read('config.ini')

# # Running code
# df = merge_data(path = params['data']['scratch'])
