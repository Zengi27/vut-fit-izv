#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
import os

def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    return geopandas.GeoDataFrame(df,
                                  geometry=geopandas.points_from_xy(df['d'], df['e']),
                                  crs='EPSG:5514')


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):

    gdf = gdf[['p1', 'p36', 'p2a', 'region', 'geometry']]
    gdf = gdf[gdf['region'] == 'JHM']
    gdf['p2a'] = pd.DatetimeIndex(gdf['p2a']).year

    gdf = gdf.to_crs("epsg:3857")

    fig, axes = plt.subplots(3,2, figsize=(12, 7))

    color = ['green', 'red']
    titles = ['JHM kraj: dalnice', 'JHM kraj: silnice prvni tridy']

    year = 2018
    for i in range(0, 3):
        gdf_tmp = gdf[gdf['p2a'] == (year + i)] 
        for j in range(0, 2):
            gdf_tmp[gdf_tmp['p36'] == j].plot(ax=axes[i][j],
                                              markersize=0.8,
                                              color=color[j])
            ctx.add_basemap(axes[i][j], 
                            crs=gdf_tmp.crs.to_string(), 
                            source=ctx.providers.Stamen.TonerLite, 
                            alpha=0.9,
                            attribution_size=5)
            
            title = titles[j] + ' (' + str(year + i) + ')'
            axes[i][j].set_title(title)
            axes[i][j].axis('off')
            axes[i][j].set_aspect('auto')
            
    if fig_location is not None:
        dir_name = os.path.dirname(fig_location)

        if dir_name:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        plt.savefig(fig_location)

    if show_figure:
        plt.show()

    
def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
