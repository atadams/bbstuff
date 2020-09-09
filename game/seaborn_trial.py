import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def clean(serie):
    output = serie[(np.isnan(serie) == False) & (np.isinf(serie) == False)]
    return output


sns.set(style="darkgrid")

player_id = 425844
player_type = 'pitcher'
year = '2020'

url = f'https://baseballsavant.mlb.com/feed?evp=true&csv=true&hfGT=R%7C&hfSea={year}%7C&player_type={player_type}&{player_type}s_lookup[]={player_id}&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_pas=0&type=details&player_id={player_id}'

df = pd.read_csv(url)

# sns.relplot(x='plate_x', y='plate_z', data=df)

# with sns.axes_style("white"):
#     sns.jointplot(x='plate_x', y='plate_z', data=df, kind="kde")

ff = df.loc[df['pitch_type'] == 'FF']
cu = df.loc[df['pitch_type'] == 'CU']
ch = df.loc[df['pitch_type'] == 'CH']
sl = df.loc[df['pitch_type'] == 'SL']
si = df.loc[df['pitch_type'] == 'SI']
print()

# sns.distplot(df['release_speed'], color="r", label='FF', hist=False)

ax = sns.distplot(ff['release_speed'], color="r", label='FF', hist=False, bins=30, )
sns.distplot(cu['release_speed'], color="b", label='CU', hist=False, bins=30, ax=ax )
sns.distplot(ch['release_speed'], color="g", label='CH', hist=False, bins=30, ax=ax )
sns.distplot(sl['release_speed'], color="y", label='SL', hist=False, bins=30, ax=ax )
sns.distplot(si['release_speed'], color="purple", label='SI', hist=False, bins=30, ax=ax )

ax.autoscale()

plt.show()

print(ff)
