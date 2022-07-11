#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import argparse
import os

from download import DataDownloader


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    

    accident_cause = ["Přerušovaná žlutá", "Semafor mimo provoz", 
                      "Dopravními značky", "Přenosné dopravní značky", "Nevyznačena", "Žádná úprava"]

    # get type of regions from data_source
    regions = np.unique(data_source["region"])
    
    # type of accident in numeric value (column p24)
    accident_types = np.unique(data_source["p24"])

    # array for count of accident
    absolut_data = []
    relative_data = []

    # iterate through types of accident
    for cause in range(len(accident_types)) :
        tmp_arr = []
        arr_in_percentage = []
        counter = 0

        # iterate through regions
        for curr_reg in range(len(regions)) :
            x = np.argwhere((data_source["region"] == regions[curr_reg]) & (data_source["p24"] == cause))
            
            tmp_arr.append(len(x))
            
            # count of accident for one of couse
            counter += len(x)

        absolut_data.append(tmp_arr)

        # convert number into percentages 
        for num in tmp_arr :
            if num == 0 :
                arr_in_percentage.append(np.nan)
            else :
                arr_in_percentage.append(num / counter * 100)
        
        relative_data.append(arr_in_percentage)

    # put "Zadna uprava" to end of array 
    relative_data.append(relative_data[0])
    relative_data.remove(relative_data[0])

    absolut_data.append(absolut_data[0])
    absolut_data.remove(absolut_data[0])

    
    fig, ax = plt.subplots(2)
    fig.set_figheight(8.27)
    fig.set_figwidth(11.69)

    # setting of first plot 
    im_0 = ax[0].imshow(absolut_data, cmap="viridis", norm=colors.LogNorm(vmax=10**5))

    cbar_0 = plt.colorbar(im_0, fraction=0.046, pad=0.04, ax=ax[0])
    cbar_0.ax.set_ylabel("Počet nehod")

    # get and set number of items in x-axis and y-axis
    ax[0].set_xticks(np.arange(len(regions)))
    ax[0].set_yticks(np.arange(len(accident_cause)))

    # setting names of axis
    ax[0].set_xticklabels(regions)
    ax[0].set_yticklabels(accident_cause)

    ax[0].set_title("Absolutně")


    # setting of second plot
    im_1 = ax[1].imshow(relative_data, cmap="plasma")

    cbar_1 = plt.colorbar(im_1, fraction=0.046, pad=0.04, ax=ax[1])
    cbar_1.ax.set_ylabel("Podíl nehod pro danou príčinu [%]")

    # get and set number of items in x-axis and y-axis
    ax[1].set_xticks(np.arange(len(regions)))
    ax[1].set_yticks(np.arange(len(accident_cause)))

    # setting names of axis
    ax[1].set_xticklabels(regions)
    ax[1].set_yticklabels(accident_cause)

    ax[1].set_title("Relativně vuči příčine")
    fig.tight_layout()

    # save graph into folder 
    if fig_location is not None :
        dir_name = os.path.dirname(fig_location)

        if not os.path.isdir(dir_name) :
            os.makedirs(dir_name)

        plt.savefig(fig_location)        

    if show_figure == True :
        plt.show()


if __name__ == "__main__" :
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--fig_location", help="Path for store figure")
    arg_parser.add_argument("--show_figure", action="store_true", help="Show figure in pop-up window")

    args = arg_parser.parse_args()

    data_source = DataDownloader().get_dict()

    plot_stat(data_source, fig_location=args.fig_location, show_figure=args.show_figure)
