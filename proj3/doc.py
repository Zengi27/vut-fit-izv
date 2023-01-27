import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


def preprocessing(df: pd.DataFrame):
    df = df[['p1', 'p12', 'p13a', 'p36', 'region']]

    # necessary data for mortality in regions
    mortality_reg = df.groupby(['region']).agg({'p13a': 'sum'}).reset_index()

    # necessary data for the most common cause of accidents
    df = df.loc[df['p13a'] > 0]
    
    df.loc[df['p12'] > 600, 'p12'] = 6
    df.loc[(df['p12'] > 500) & (df['p12'] < 517), 'p12'] = 5
    df.loc[(df['p12'] > 400) & (df['p12'] < 415), 'p12'] = 4
    df.loc[(df['p12'] > 300) & (df['p12'] < 312), 'p12'] = 3
    df.loc[(df['p12'] > 200) & (df['p12'] < 210), 'p12'] = 2
    df.loc[(df['p12'] == 100), 'p12'] = 1

    data_type_of_traffic = df.groupby(['p12', 'p36']).agg({'p13a': 'sum'})
    data_type_of_traffic = data_type_of_traffic.reset_index()

    df = df.groupby(['p12']).agg({'p13a': 'sum'}).reset_index()
    
    df = df.set_index('p12')
    df = df.rename({1: 'Nezavinené vodičom',
                    2: 'Neprimeraná rýchlosť jazdy',
                    3: 'Nesprávne predbiehanie',
                    4: 'Nedanie prednosti v jazde',
                    5: 'Nesprávny zpôsob jazdy',
                    6: 'technická závada vozidla'}).reset_index()

    cause_of_the_accident = df
    
    data = [mortality_reg, 
            cause_of_the_accident,
            data_type_of_traffic]
    
    return data


def plot_cause_of_accident(df: pd.DataFrame, fig_location, show_figure: bool = False):
    fig, ax = plt.subplots(figsize=(10, 8.27))
    g = sns.barplot(ax=ax,
                    data=df,
                    x='p13a',
                    y='p12',
                    orient='h',
                    palette='pastel')

    g.set_title('Hlavna príčina umrtia pri nehode', fontsize=16)
    g.set_xlabel("Počet nehôd", fontsize=14)
    g.set_ylabel("Príčina nehody", fontsize=14)
    g.bar_label(g.containers[0])
    
    plt.tight_layout()
    plt.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_region_mortality(df: pd.DataFrame, fig_location, show_figure: bool = False):
    fig, ax = plt.subplots(figsize=(8.40, 8.27))
    g = sns.barplot(ax=ax,
                    data=df,
                    x='region',
                    y='p13a',
                    orient='v',
                    palette='pastel')
    
    g.set_title('Počet úmrtí v jednotlivých krajoch', fontsize=16)
    g.set_xlabel("Kraj", fontsize=14)
    g.set_ylabel("počet umrtí", fontsize=14)
    g.bar_label(g.containers[0])
    
    plt.tight_layout()
    plt.savefig(fig_location)

    if show_figure:
        plt.show()


def make_table(df: pd.DataFrame):
    df = df.set_index('p12')
    df = df.rename({1: 'Nezavinené vodičom',
                    2: 'Neprimeraná rýchlosť jazdy',
                    3: 'Nesprávne predbiehanie',
                    4: 'Nedanie prednosti v jazde',
                    5: 'Nesprávny zpôsob jazdy',
                    6: 'technická závada vozidla'}).reset_index()
    
    df = df.set_index('p36')
    df = df.rename({0: 'dialnica',
                    1: 'cesta 1. triedy',
                    2: 'cesta 2. triedy',
                    3: 'cesta 3. triedy',
                    4: 'uzol',
                    5: 'komunikácia sledovaná',
                    6: 'komunikácia miestna',
                    7: 'komunikácia účelová',
                    8: 'komunikácia účelová'}).reset_index()
    
    df = pd.pivot_table(df, columns='p12', values='p13a', index='p36', fill_value=0)
    df = df.astype(int)

    df.to_excel('table.xlsx')
    

def print_stats(df: pd.DataFrame):
    num_of_accident = df.shape[0]
    df = df.loc[df['p13a'] > 0]

    num_of_death = df['p13a'].sum()
    pst_of_death = num_of_death / num_of_accident * 100
    
    avg_mortality = num_of_death / 14 
    
    print("Pocet nehod: ", num_of_accident)
    print("Pocet umrti: ", num_of_death)
    print("Umrtnost: {:.2f} %".format(pst_of_death))
    print("Priemerna umrtnost v krajoch: {:.2f} ".format(avg_mortality))
    print("Umrtnost v STC kraji je 2.33 krat vacia nez priemer")
    print("Umrtnost v STC je 6.24 krat vacsia ako v KVK")
    print("Najcastejsia pricina je nespravny sposob jazdy co predstavuje az 38%")
    print("Na ceste 2. a 3. triedy byva najcastesia pricina umrtia neprimerana rychlost jazdy")
    
    
if __name__ == "__main__":
    dataframe = pd.read_pickle("accidents.pkl.gz")
    
    data = preprocessing(dataframe)

    plot_region_mortality(data[0], 'fig1', show_figure=True)    
    plot_cause_of_accident(data[1], 'fig2', show_figure=True)
    make_table(data[2])
    print_stats(dataframe)
    