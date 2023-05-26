import pandas as pd
from os import path
sDateTimeFormat = '%Y/%m/%d'
sOutputFileName = 'Swaps_Processed.csv'
sBasePath = 'C:\\Users\\franc\\Documents\\MetaTrader_tests\\Swaps'
sOutputFilePath = path.join(sBasePath,sOutputFileName)
if __name__ == '__main__':
    # from https://www.fibogroup.eu/products/account-types/swap-history/

    sFileName = 'swaps.xlsx'
    sFilePath = path.join(sBasePath,sFileName)
    df_dataframe = pd.read_excel(sFilePath, sheet_name=None,header = None)
    df_dataframe = pd.concat(df_dataframe, axis=0)
    df_dataframe = df_dataframe.reset_index()
    df_dataframe.drop(columns=df_dataframe.columns[0:2], axis=1, inplace=True)
    df_dataframe.columns = ['Pair','dTime','Long','Short']
    df_dataframe ['Pair'] = df_dataframe ['Pair'] .replace('/', '_', regex=True)
    df_dataframe = df_dataframe.groupby(['dTime', 'Pair']).mean()


    df_dataframe[['dTime', 'Pair']] = pd.DataFrame(df_dataframe.index.tolist(),index = df_dataframe.index)
    df_dataframe = df_dataframe[["dTime", "Pair", "Long","Short"]]
    df_dataframe.reset_index(drop=True, inplace=True)
    df_dataframe['dTime'] = df_dataframe['dTime'].apply(lambda x: x.strftime(sDateTimeFormat))
    df_dataframe['Pair'] = df_dataframe['Pair'].str.replace('_', '')
    df_dataframe.to_csv(sOutputFilePath,sep = ";")
    # process swap file into one csv file