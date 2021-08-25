# Load the Pandas libraries with alias 'pd' 
import pandas as pd 

# for filename matching
import fnmatch
import os

# save into a new df
# object With column names only
df = pd.DataFrame(columns = ['sc', 'id_len', 'speed_mean_avg', 'speed_std_avg', 'throughput', 'lc_count', 'ZOV_density'])
print(df) 

# subdir = "%02d" % 0

# df = df.append({'sc' : int(subdir), 'throughput': 1, 'lc_count' : 2, 'ZOV_density' : 3},
#                 ignore_index = True )   
# print(df)

# if int(subdir) in df.values:
#     row_id = df.sc[df.sc == int(subdir)].index.tolist()
#     print(row_id)

# data = pd.read_csv("sc03/highway-ramp_20210718-1024591626618299.1339302-0_emission.csv")
# data.info()

# data = pd.read_csv('sc03/' + 'highway-ramp_20210718-1024591626618299.1339302-0_emission.csv')
# data.info()

# auto-run for all scenarios 
for i in range(36,37):
    subdir = "%02d" % i
    print(subdir)
    for file in os.listdir('./sc'+subdir):
        if fnmatch.fnmatch(file, '*_crystal.csv'):
            print(file)
            print('crystal' + subdir)

            # try:
            #     data = pd.read_csv('sc' + subdir + '/' + file)
            # except OSError:
            #     print("no file")
            #     pass

            data = pd.read_csv('sc' + subdir + '/' + file)
            #data.info()

            # Group data by id and summarize speed column
            measures_by_info = data.groupby('info')
            #print(measures_by_info.describe())

            # cal throughput of steady state: 3000 for warmup, total 6000
            thr_col = measures_by_info.get_group('throughput')
            # print(thr_col)
            # print(thr_col.iloc[3000:])
            # print(thr_col.iloc[3000,2])
            # print(thr_col.iloc[6000,2])
            thr_steady = thr_col.iloc[6000,2] - thr_col.iloc[3000,2]
            # print(thr_steady)

            # cal ZOV lane density for utilization of steady state: 3000 for warmup, total 6000
            uti_col = measures_by_info.get_group('num_zov_on_zov_lane')
            # print(uti_col)
            # print(uti_col.iloc[3000:])
            # print(uti_col.iloc[3000,2])
            # print(uti_col.iloc[6000,2])
            uti_steady = sum(uti_col.iloc[3000:6000,2])/3001
            # print(uti_steady)

            # cal lane change count of steady state: 3000 for warmup, total 6000
            lc_col = measures_by_info.get_group('num_lane_change')
            # print(lc_col)
            # print(lc_col.iloc[3000:])
            # print(lc_col.iloc[3000,2])
            # print(lc_col.iloc[6000,2])
            lc_count_steady = lc_col.iloc[6000,2] - lc_col.iloc[3000,2]
            # print(lc_count_steady)
            
            if int(subdir) in df.values:
                row_id = df.sc[df.sc == int(subdir)].index.tolist()
                print(row_id)

                df.at[row_id, 'throughput'] = thr_steady
                df.at[row_id, 'lc_count'] = lc_count_steady
                df.at[row_id, 'ZOV_density'] = uti_steady
                print(df)

            else:
            # append rows to an empty DataFrame
                df = df.append({'sc' : int(subdir), 'throughput': thr_steady, 'lc_count' : lc_count_steady, 'ZOV_density' : uti_steady},
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

            data = pd.read_csv('sc' + subdir + '/' + file)

            # # Preview the first 5 lines of the loaded data 
            # data.head()
            # data.info()

            # # calculation
            # data[["speed"]].describe()
            # print(data["speed"].describe())

            # Group data by id and summarize speed column
            emission_by_id = data.groupby(["id"])[["speed"]].describe()
            # print(emission_by_id)
            # print(emission_by_id.shape[0])

            # retrieving all rows and some columns by iloc method 
            all_mean = emission_by_id.iloc [:, 1]
            #print(all_mean)
            all_mean_avg = all_mean.mean()
            #print(all_mean_avg)

            all_std = emission_by_id.iloc [:, 2]
            #print(all_std)
            all_std_avg = all_std.mean()
            #print(all_std_avg)

            if int(subdir) in df.values:
                row_id = df.sc[df.sc == int(subdir)].index.tolist()
                print(row_id)
            
                df.at[row_id, 'id_len'] = emission_by_id.shape[0]
                df.at[row_id, 'speed_mean_avg'] = all_mean_avg
                df.at[row_id, 'speed_std_avg'] = all_std_avg
                print(df)

            else:
                # append rows to an empty DataFrame
                df = df.append({'sc' : int(subdir), 'id_len' : emission_by_id.shape[0], 'speed_mean_avg' : all_mean_avg, 'speed_std_avg' : all_std_avg},
                                ignore_index = True )
                print(df)
            
            
            del data
            del emission_by_id
            del all_mean
            del all_std
            # data.info()

        