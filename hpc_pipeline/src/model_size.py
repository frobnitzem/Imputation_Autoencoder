""" Manually run script to summarize the model
    numbers and disk sizes.
"""
import pandas as pd

df = pd.read_csv('model_size.csv', sep=' ')
df = df.loc[df['kbytes'] > 10] # only report on models larger than 10kb

sz = df.groupby('chr').mean()
print(sz['kbytes'])
print(df.groupby('chr').count()['model'])

ntile = dict((c,len(df.loc[df['chr'] == c]['tile'].unique()))
             for c in df['chr'].unique())

print("Number of tiles")
print(ntile)
