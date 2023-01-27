#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)

    # columns for category
    category_cols = ['p36', 'p5a', 'weekday(p2a)', 'p6', 'p7', 'p8', 'p9', 'p10',
                     'p11', 'p12', 'p13a', 'p13b', 'p13c', 'p15', 'p16', 'p17',
                     'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27',
                     'p28', 'p34', 'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a',
                     'p49', 'p50a', 'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57',
                     'p58', 'j', 'o', 'p', 't']

    if verbose:
        orig_size = df.memory_usage(deep=True).sum() / 1048576

    # rename column 'p2a' to 'date'
    df.rename(columns={'p2a': 'date'}, inplace=True)

    # change data type
    for col in df.columns:
        if col == 'date':
            df[col] = df[col].astype('datetime64')
        elif col in category_cols:
            df[col] = df[col].astype('category')

    # print memory usage 
    if verbose:
        new_size = df.memory_usage(deep=True).sum() / 1048576
        print(f"orig_size={orig_size:.1f} MB")
        print(f"new_size={new_size:.1f} MB")

    return df


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):

    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(8.27, 8.27))
    # tmp array of axes 
    axs = [ax1, ax2, ax3, ax4, ax5, ax6]
    # tmp array from title labels
    headers = ['dvoupruhová komunikace', 'třípruhová komunikace',
               'čtyřpruhová komunikace', 'vícepruhová komunika',
               'rychlostní komunikace', 'jiná komunikace']

    df = df[['p21', 'region']].set_index('region')
    df = df.loc[['JHM', 'PHA', 'STC', 'VYS']].reset_index()

    # column for easy count of accident
    df['tmp'] = 1

    df = pd.pivot_table(df, columns='p21', values='tmp', index='region', aggfunc="sum")

    # add columns 3 and 4
    df[3] = df[3] + df[4]
    # delete 4th column
    df = df.drop(columns=4)
    # switch first and last column 
    df = df[[1, 2, 3, 5, 6, 0]]

    fig.suptitle('Druhy silnic')
    sns.set_theme(style='white', palette='pastel')
    for i, col in enumerate(df):
        axs[i].set_title(headers[i])
        sns.barplot(ax=axs[i], data=df,
                    x=df.index, y=df.columns[i])

        # set Y-labels
        if i in [0, 3]:
            axs[i].set_ylabel('Počet nehod')
        else:
            axs[i].set_ylabel('')

        # set X-labels
        if i in [3, 4, 5]:
            axs[i].set_xlabel('Kraj')
        else:
            axs[i].set_xlabel('')

    plt.tight_layout()

    # Save figure into location
    if fig_location is not None:
        dir_name = os.path.dirname(fig_location)

        if dir_name:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        plt.savefig(fig_location)

    # plot figure
    if show_figure:
        plt.show()


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):

    df = df[['p58', 'p10', 'date', 'region']].set_index('region')
    df = df.loc[['PHA', 'JHM', 'STC', 'VYS']].reset_index()
    df = df[df['p58'] == 5]

    # extracting year and month from DataTime
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    # make tmp column for counting value
    df['tmp'] = 1

    df = df[df['year'] != 2021]
    df = df.drop(columns=['date', 'year', 'p58'])

    df = df.set_index('p10')
    # rename index for better visualization
    df = df.rename(index={1: 'řidičem', 2: 'řidičem', 3: 'jiné',
                          4: 'zvěří', 5: 'jiné', 6: 'jiné',
                          7: 'jiné', 0: 'jiné'
                          })

    df = df.reset_index()
    df = df.groupby(['region', 'month', 'p10']).agg('count')
    df = df.reset_index()

    sns.set_theme(style='darkgrid', palette='pastel')
    g = sns.catplot(x='month', y='tmp', col='region', data=df,
                    kind='bar', hue='p10', col_wrap=2,
                    sharey=False)

    g.set_axis_labels("Měsíc", "Počet nehod")
    g.set_titles("Kraj: {col_name}")
    g._legend.set_title("Zavinění")

    # save figure into location
    if fig_location is not None:
        dir_name = os.path.dirname(fig_location)

        if dir_name:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        plt.savefig(fig_location)

    # show figure
    if show_figure:
        plt.show()


def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):

    df = df[['p18', 'date', 'region']].set_index('region')
    df = df.loc[['PHA', 'JHM', 'STC', 'VYS']].reset_index()
    df = df[df['p18'] != 0]
    df = df[df['date'].dt.year != 2021]
    # make tmp column for counting value
    df['tmp'] = 1

    df = df.set_index('p18')
    # rename index for better visualization
    df = df.rename({1: 'neztížené', 2: 'mlha', 3: 'na počátku deště',
                    4: 'déšť', 5: 'sněžení', 6: 'náledí',
                    7: 'vítr'}).reset_index()

    df = pd.pivot_table(df, columns=['p18'], values='tmp', index=['date', 'region'], aggfunc='sum')
    df = df.reset_index().set_index('date')
    df = df.groupby('region').resample('M').sum()

    df = df.stack()
    df = df.reset_index()

    facet_kws = {'sharey': False, 'sharex': False}
    sns.set_theme(style='darkgrid', palette='pastel')

    # make line plot 
    g = sns.relplot(x='date', y=0, data=df, kind='line',
                    hue='p18', col='region', col_wrap=2,
                    facet_kws=facet_kws)

    # set labels and titles
    g.set_axis_labels("Rok", "Počet nehod")
    g.set_titles("Kraj: {col_name}")
    g._legend.set_title("Podmínky")

    # save figure into location
    if fig_location is not None:
        dir_name = os.path.dirname(fig_location)

        if dir_name:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        plt.savefig(fig_location)

    # show figure
    if show_figure:
        plt.show()


if __name__ == "__main__":
    dataframe = get_dataframe("accidents.pkl.gz", verbose=True)

    # plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    # plot_animals(df, "02_animals.png", True)
    plot_conditions(dataframe, "03_conditions.png", True)
