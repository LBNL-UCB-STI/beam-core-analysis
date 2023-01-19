# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

outdir = '~/Desktop/git/beam/output/sf-light/'
filename = '/ITERS/it.0/0.skimsRidehail.csv.gz'

sk5 = pd.read_csv(outdir + 'urbansim-10k-05pctAccessible' + filename)
sk10 = pd.read_csv(outdir + 'urbansim-10k-10pctAccessible' + filename)
sk20 = pd.read_csv(outdir + 'urbansim-10k-20pctAccessible' + filename)
sk30 = pd.read_csv(outdir + 'urbansim-10k-30pctAccessible' + filename)
sk35 = pd.read_csv(outdir + 'urbansim-10k-35pctAccessible' + filename)
sk40 = pd.read_csv(outdir + 'urbansim-10k-40pctAccessible' + filename)
sk45 = pd.read_csv(outdir + 'urbansim-10k-45pctAccessible' + filename)
sk50 = pd.read_csv(outdir + 'urbansim-10k-50pctAccessible' + filename)


# %%
def fill(df):
    df['completedRequests'] = (100.0 - df['unmatchedRequestsPercent']) * df['observations'] / 100.
    df['totalWaitTime'] = (df['waitTime'] * df['completedRequests']).fillna(0)
    return df


sk5 = fill(sk5)
sk10 = fill(sk10)
sk20 = fill(sk20)
sk30 = fill(sk30)
sk35 = fill(sk35)
sk40 = fill(sk40)
sk45 = fill(sk45)
sk50 = fill(sk50)

# %%

# sns.distplot(..., hist_kws={'weights': your weights array}, ...)

f, (ax1, ax2, ax3) = plt.subplots(1, 3)
sns.histplot(sk5, x='waitTime', hue='wheelchairRequired', stat='probability', weights='observations', common_norm=False,
             bins=20, ax=ax1)
sns.histplot(sk20, x='waitTime', hue='wheelchairRequired', stat='probability', weights='observations',
             common_norm=False, bins=20, ax=ax2)
sns.histplot(sk40, x='waitTime', hue='wheelchairRequired', stat='probability', weights='observations',
             common_norm=False, bins=20, ax=ax3)


# %%

def stats(df):
    df['completedRequests'] = (100 - df['unmatchedRequestsPercent']) * df['observations'] / 100.
    meanWaitTime = df['totalWaitTime'].sum() / df['completedRequests'].sum()
    completedFraction = df['completedRequests'].sum() / df['observations'].sum()
    portionOfRidesByAccessibleVehicles = (df['completedRequests'] * df['accessibleVehiclesPercent']).sum() / df[
        'completedRequests'].sum()
    return (meanWaitTime, completedFraction, portionOfRidesByAccessibleVehicles)


wt5all, cf5all, acc5all = stats(sk5)
wt10all, cf10all, acc10all = stats(sk10)
wt20all, cf20all, acc20all = stats(sk20)
wt30all, cf30all, acc30all = stats(sk30)
wt35all, cf35all, acc35all = stats(sk35)
wt40all, cf40all, acc40all = stats(sk40)
wt45all, cf45all, acc45all = stats(sk45)
wt50all, cf50all, acc50all = stats(sk50)
wt5wc, cf5wc, acc5wc = stats(sk5.loc[sk5.wheelchairRequired])
wt10wc, cf10wc, acc10wc = stats(sk10.loc[sk10.wheelchairRequired])
wt20wc, cf20wc, acc20wc = stats(sk20.loc[sk20.wheelchairRequired])
wt30wc, cf30wc, acc30wc = stats(sk30.loc[sk30.wheelchairRequired])
wt35wc, cf35wc, acc35wc = stats(sk35.loc[sk35.wheelchairRequired])
wt40wc, cf40wc, acc40wc = stats(sk40.loc[sk40.wheelchairRequired])
wt45wc, cf45wc, acc45wc = stats(sk45.loc[sk45.wheelchairRequired])
wt50wc, cf50wc, acc50wc = stats(sk50.loc[sk50.wheelchairRequired])
wt5no, cf5no, acc5no = stats(sk5.loc[~sk5.wheelchairRequired])
wt10no, cf10no, acc10no = stats(sk10.loc[~sk10.wheelchairRequired])
wt20no, cf20no, acc20no = stats(sk20.loc[~sk20.wheelchairRequired])
wt30no, cf30no, acc30no = stats(sk30.loc[~sk30.wheelchairRequired])
wt35no, cf35no, acc35no = stats(sk35.loc[~sk35.wheelchairRequired])
wt40no, cf40no, acc40no = stats(sk40.loc[~sk40.wheelchairRequired])
wt45no, cf45no, acc45no = stats(sk45.loc[~sk45.wheelchairRequired])
wt50no, cf50no, acc50no = stats(sk50.loc[~sk50.wheelchairRequired])

# %%
x = [0.05, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5]
plt.subplot(121)
plt.scatter(x, [cf5wc, cf10wc, cf20wc, cf30wc, cf35wc, cf40wc, cf45wc, cf50wc], label='Wheelchair')
plt.scatter(x, [cf5no, cf10no, cf20no, cf30no, cf35no, cf40no, cf45no, cf50no], label='Non-Wheelchair')
plt.xlabel('Portion of fleet wheelchair accessible')
plt.ylabel('Portion of requests successfully matched')

plt.subplot(122)
plt.scatter(x, [wt5wc, wt10wc, wt20wc, wt30wc, wt35wc, wt40wc, wt45wc, wt50wc], label='Wheelchair')
plt.scatter(x, [wt5no, wt10no, wt20no, wt30no, wt35no, wt40no, wt45no, wt50no], label='Non-Wheelchair')
plt.legend()
plt.xlabel('Portion of fleet wheelchair accessible')
plt.ylabel('Mean wait time (sec)')
