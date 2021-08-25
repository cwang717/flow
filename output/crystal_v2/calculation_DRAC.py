############################
# calculate DRAC
##########################

# Load the Pandas libraries with alias 'pd' 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import math

# for filename matching
import fnmatch
import os


# save into a new df
# object With column names only
df = pd.DataFrame(columns = ['sc', 'conflict', 'conflict_2'])
print(df) 

# auto-run for all scenarios 
for i in range(36,39):
#for i in [15, 16, 17]:
    subdir = "%02d" % i
    print(subdir)
    for file in os.listdir('./output/crystal_v2/sc'+subdir):

        if fnmatch.fnmatch(file, '*_emission.csv'):
            print(file)
            print('emission' + subdir)

            data = pd.read_csv('./output/crystal_v2/sc' + subdir + '/' + file)
            data_new = data[['time','id','x','y','lane_number','leader_id','speed','headway','leader_rel_speed']].copy()
            # print(data.describe())
            # print(data.head(5))
            data_filtered_0 = data_new[data['time'] > 300].copy() #steady state
            # print(data_filtered_0.head(5))
            #print(data_filtered_0.describe())
            data_filtered_1 = data_filtered_0.dropna(subset=['time','leader_id']) # delete no-leader data
            data_filtered_2 = data_filtered_1[data_filtered_1['speed'] >= 0].copy() # eliminate outlier 
            data_filtered_3 = data_filtered_2[data_filtered_2['headway'] >= 0].copy() # hard to fix in simulation
            data_filtered_4 = data_filtered_3[data_filtered_3['leader_rel_speed'] < 0].copy() 
            #print(data_filtered_4.describe())
            data_filtered =  data_filtered_4[data_filtered_4['lane_number'] != 0].copy() 
            # print(data_filtered_3.shape[0])
            # print(data_filtered.shape[0])
            # print(data_filtered.describe())
            
            #leader_str = data_filtered.iloc[:,6].str[8:19]
            leader_str = data_filtered.loc[:,'leader_id'].str[8:19].copy()
            data_filtered.loc[:,'leader_type'] = ['HDV-' if 'hum' in x else 'CAV-' for x in leader_str]
            #follower_str = data_filtered.iloc[:,1].str[8:19]
            follower_str = data_filtered.loc[:,'id'].str[8:19].copy()
            data_filtered.loc[:,'follower_type'] = ['HDV' if 'hum' in x else 'CAV' for x in follower_str]
            data_filtered.loc[:,'LF_type'] = data_filtered['leader_type'].copy() + data_filtered['follower_type'].copy()
            #print(data_filtered.head(5))
            #print(data_filtered['LF_type'].describe())

            data_filtered['DRAC'] = 0.5 * data_filtered['leader_rel_speed'].copy() ** 2 / data_filtered['headway'].copy()
            print(data_filtered['DRAC'].describe())

            ## count conflict using DRAC
            data_filtered['conflict'] =''
            data_filtered.loc[(i % 3 == 2) & (data_filtered['lane_number'] ==3) & (data_filtered['DRAC'] > 7.9), 'conflict'] = 0
            data_filtered.loc[(i % 3 == 2) & (data_filtered['lane_number'] ==3) & (data_filtered['DRAC'] <= 7.9), 'conflict'] = 1
            data_filtered.loc[(i % 3 == 2) & (data_filtered['lane_number'] !=3) & (data_filtered['DRAC'] > 3.4), 'conflict'] = 2
            data_filtered.loc[(i % 3 == 2) & (data_filtered['lane_number'] !=3) & (data_filtered['DRAC'] <= 3.4), 'conflict'] = 3
            data_filtered.loc[(i % 3 != 2) & (data_filtered['DRAC'] > 3.4), 'conflict'] = 4
            data_filtered.loc[(i % 3 != 2) & (data_filtered['DRAC'] <= 3.4), 'conflict'] = 5         

            # ## count conflict using DRAC
            # data_filtered['conflict'] =''
            # data_filtered.loc[data_filtered['DRAC'] > 3.4, 'conflict'] = 1
            # data_filtered.loc[data_filtered['DRAC'] <= 3.4, 'conflict'] = 0

            # print(data_filtered.head(5))

            # conflict_by_LF = data_filtered.groupby(["LF_type",'conflict'])[["conflict"]].describe()
            # print(conflict_by_LF)
            conflict_by_value = data_filtered.groupby(['conflict'])[["conflict"]].describe()
            print(conflict_by_value)

            # conflict_rate = conflict_by_value.iloc [1,0] / (conflict_by_value.iloc [0,0] + conflict_by_value.iloc [1,0])
            # print(conflict_rate)
            # # dom: all times
            # conflict_rate_2 = conflict_by_value.iloc [1,0] / data_filtered_3.shape[0]
            # print(conflict_rate_2)
            

            # df = df.append({'sc' : i, 'conflict' : conflict_rate, 'conflict_2' : conflict_rate_2},
            #                     ignore_index = True )   
            # print(df)

            # #box plot
            # boxplot = data_filtered.boxplot(column='headway', by='LF_type')
            # plt.show()
            # boxplot = data_filtered.boxplot(column='leader_rel_speed', by='LF_type')
            # plt.show()
            # boxplot = data_filtered.boxplot(column='TTC', by='LF_type')
            # plt.show()
            # #plt.savefig("ttc_" +'sc' + subdir + ".png")

                    
            del data
            del data_filtered
            del data_filtered_0
            del data_filtered_1
            del data_filtered_2
            del data_new
            del leader_str
            del follower_str
            del conflict_by_value

            # data.info()

        