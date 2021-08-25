############################
# calculate other measures
##########################

# Load the Pandas libraries with alias 'pd' 
import pandas as pd 

# for filename matching
import fnmatch
import os

# save into a new df
# object With column names only
df = pd.DataFrame(columns = ['sc', 'speed_mean_avg', 'throughput', 'speed*thr', 'ZOV_density', 'special_lane_throughput','speed_std_avg', 'lc_count', 'lc_cav_perc' ])
print(df) 


# auto-run for all scenarios 
for i in range(30,33):
#for i in [0, 13,14]:
    subdir = "%02d" % i
    print(subdir)
    for file in os.listdir('./output/crystal_v2/sc'+subdir):
        if fnmatch.fnmatch(file, '*_crystal.csv'):
            print(file)
            print('crystal' + subdir)

            # try:
            #     data = pd.read_csv('sc' + subdir + '/' + file)
            # except OSError:
            #     print("no file")
            #     pass

            data = pd.read_csv('./output/crystal_v2/sc' + subdir + '/' + file)
            print(data.info())

            # Group data by id and summarize speed column
            measures_by_info = data.groupby('info')
            #print(measures_by_info.describe())

            # cal throughput of steady state: 3000 for warmup, total 9000
            thr_col = measures_by_info.get_group('throughput')
            # print(thr_col)
            # print(thr_col.iloc[3000:])
            # print(thr_col.iloc[3000,2])
            # print(thr_col.iloc[9000,2])
            thr_steady = thr_col.iloc[9000,2] - thr_col.iloc[3000,2]
            # print(thr_steady)

            thr_special_col = measures_by_info.get_group("special_lane_throughput")
            thr_special_steady = thr_special_col.iloc[9000, 2] - thr_special_col.iloc[3000, 2]
            
            # cal ZOV lane density for utilization of steady state: 3000 for warmup, total 9000
            uti_col = measures_by_info.get_group('num_zov_on_zov_lane')
            # print(uti_col)
            # print(uti_col.iloc[3000:])
            # print(uti_col.iloc[3000,2])
            # print(uti_col.iloc[9000,2])
            uti_steady = sum(uti_col.iloc[3000:9000,2])/3001
            # print(uti_steady)

            # cal lane change count of steady state: 3000 for warmup, total 9000
            lc_col = measures_by_info.get_group('num_lane_change')
            # print(lc_col)
            # print(lc_col.iloc[3000:])
            # print(lc_col.iloc[3000,2])
            # print(lc_col.iloc[9000,2])
            lc_count_steady = lc_col.iloc[9000,2] - lc_col.iloc[3000,2]
            # print(lc_count_steady)
            
            if i in df['sc'].values:
                row_id = df.sc[df.sc == i].index.tolist()
                #print(row_id)

                df.at[row_id, 'throughput'] = thr_steady
                df.at[row_id, 'special_lane_throughput'] = thr_special_steady
                df.at[row_id, 'lc_count'] = lc_count_steady
                df.at[row_id, 'ZOV_density'] = uti_steady
                print(df)

            else:
            # append rows to an empty DataFrame
                df = df.append({'sc' : i, 'throughput': thr_steady, 'special_lane_throughput': thr_special_steady, 'lc_count' : lc_count_steady, 'ZOV_density' : uti_steady},
                                ignore_index = True )   
                print(df)

            del data
            del thr_col
            del lc_col
            del uti_col

        if fnmatch.fnmatch(file, '*_emission.csv'):
            print(file)
            print('emission' + subdir)

            # Read data from file 'filename.csv' 
            # (in the same directory that your python process is based)
            # Control delimiters, rows, column names with read_csv (see later) 
            #data = pd.read_csv("sc00/highway-ramp_20210718-0043261626583406.8378727-0_emission.csv") 
            # try:
            #     data = pd.read_csv('sc' + subdir + '/' + file)
            # except OSError:
            #     print("no file")
            #     pass

            data = pd.read_csv('./output/crystal_v2/sc' + subdir + '/' + file)

            ## data cleaning
            data_new = data[['time','id','lane_number','speed','headway']].copy()
            print(data.describe())
            #print(data.head(5))
            data_filtered_0 = data_new[data['time'] > 300].copy()
            #print(data_filtered_0.describe())
            #print(data_filtered_0.head(5))
            data_filtered_2 = data_filtered_0[data_filtered_0['speed'] >= 0].copy()
            print(data_filtered_2.describe())
            data_filtered_4 = data_filtered_2[data_filtered_2['headway'] >= 0].copy() # hard to fix in simulation

            data_filtered_1 =  data_filtered_4[data_filtered_4['lane_number'] != 0].copy() 

        
            # Group data by id and summarize speed column
            emission_by_id = data_filtered_1.describe()
            all_mean_avg = emission_by_id.loc['mean','speed']
            all_std_avg = emission_by_id.loc['std','speed']
            #print(all_std_avg)

            ## lc by vehicle type
            # vehicle type
            follower_str = data_filtered_1.loc[:,'id'].str[8:19].copy()
            data_filtered_1.loc[:,'follower_type'] = ['HDV' if 'hum' in x else 'CAV' for x in follower_str]
            # info at next row
            data_filtered_1['lane_number_next'] = data_filtered_1['lane_number'].shift(-1) #next row
            data_filtered_1['id_next'] = data_filtered_1['id'].shift(-1)
            #print(data_filtered_1.head(10))
            # identify lane-change
            data_filtered_1['lc'] =''
            data_filtered_1.loc[(data_filtered_1['id'] == data_filtered_1['id_next']) & (data_filtered_1['lane_number'] != data_filtered_1['lane_number_next']), 'lc'] = 1
            data_filtered_1.loc[(data_filtered_1['id'] == data_filtered_1['id_next']) & (data_filtered_1['lane_number'] == data_filtered_1['lane_number_next']), 'lc'] = 0
            data_filtered_1.loc[data_filtered_1['id'] != data_filtered_1['id_next'], 'lc'] = 0
            print(data_filtered_1.head(10))
            #print(data_filtered_1.groupby(['lc','follower_type'])[["lc"]].describe())
            # count CAV lane-change over all lane-change
            lc_by_type = data_filtered_1.groupby(['lc','follower_type'])[["lc"]].describe()
            # print(lc_by_type)
            # print(lc_by_type.iloc[2,0])
            # print(lc_by_type.iloc[3,0])
            lc_cav = lc_by_type.iloc[2,0].copy() / (lc_by_type.iloc[2,0].copy() + lc_by_type.iloc[3,0].copy())
            # print(lc_cav)

            # store into df
            if i in df['sc'].values:
                row_id = df.sc[df.sc == i].index.tolist()
                print(row_id)
            
                #df.at[row_id, 'id_len'] = emission_by_id.shape[0]
                df.at[row_id, 'speed_mean_avg'] = all_mean_avg
                df.at[row_id, 'speed_std_avg'] = all_std_avg
                df.at[row_id, 'lc_cav_perc'] = lc_cav
                print(df)

            else:
                # append rows to an empty DataFrame
                df = df.append({'sc' : i, 'speed_mean_avg' : all_mean_avg, 'speed_std_avg' : all_std_avg, 'lc_cav_perc': lc_cav},
                                ignore_index = True )
                print(df)
            
            
            del data
            del emission_by_id
            # data.info()

df['speed*thr'] = df.loc[:,'speed_mean_avg'].copy() * df.loc[:,'throughput'].copy()
print(df)

        