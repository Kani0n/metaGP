#!/user/bin/env python3

import os
import pandas as pd
import skbio
import math
from itertools import combinations
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import seaborn as sns
from statannotations.Annotator import Annotator
from skbio.stats.ordination import pcoa
import numpy as np
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from skbio.stats.distance import anosim

import util, config


# filter low abundant taxa
def fiter_taxprof(taxprof, abund, preval, filtered_taxprof):
    df_taxprof = pd.read_csv(taxprof, sep='\t').set_index('clade_name')
    # filter low abundant taxa
    df_taxprof[df_taxprof < abund] = 0
    # filer low prevalent taxa
    df_prev = df_taxprof.astype(bool).sum(axis=1)
    prevalent_taxa = df_prev[df_prev > preval * df_taxprof.shape[1] * 0.01].index.to_list()
    df_taxprof_preval = df_taxprof.loc[prevalent_taxa,:]
    df_taxprof_preval.to_csv(filtered_taxprof, sep='\t')


def compute_stat(df, param, pairs):
    stat_results = []
    for each_pair in pairs:
        first = df.loc[df.subject == each_pair[0], param].values
        second = df.loc[df.subject == each_pair[1], param].values
        stat_results.append(mannwhitneyu(first, second, alternative="two-sided"))
    pvalues = [result.pvalue for result in stat_results]
    return(pvalues)


# boxplot for alpha diversity with scatter and significat marker
def boxplot(ax, df, x_val, y_val, pairs):
    ax.set(ylim=(df[y_val].min(axis=0)-1, df[y_val].max(axis=0) + 1))
    sns.boxplot(ax=ax, data=df, x=x_val, y=y_val)
    sns.swarmplot(ax=ax, x=x_val, y=y_val, data=df, color="#454B1B", edgecolor='white', linewidth=0.5, size=5, alpha=0.7)
    annotator = Annotator(ax, pairs, data=df, x=x_val, y=y_val)
    annotator.configure(test='Mann-Whitney', loc='inside', text_format='star')
    annotator.apply_and_annotate()


def compute_alpha_diversity(abundance_file, metafile, sample, column, outdir):
    abun_tab = pd.read_csv(abundance_file, sep='\t')
    abun_tab = abun_tab.drop('clade_name', axis=1)
    abun_tab = abun_tab.T
    ids = abun_tab.index.to_list()

    # Richness
    richness = skbio.diversity.alpha_diversity('observed_otus', abun_tab, ids).to_list()
    # Shannon index
    shannon = skbio.diversity.alpha_diversity('shannon', abun_tab, ids).to_list()
    # Shannon effective index
    shannon_effective = [math.exp(i) for i in shannon]
    # Simpson index
    simpson = skbio.diversity.alpha_diversity('simpson', abun_tab, ids).to_list()
    # Simpson effective index
    simpson_effective = [1./i for i in simpson]
    # Simpson_evenness
    simpson_e = skbio.diversity.alpha_diversity('simpson_e', abun_tab, ids).to_list()
    # Gini_index
    gini_index = skbio.diversity.alpha_diversity('gini_index', abun_tab, ids).to_list()
    all_param = ['Richness', 'Shannon index', 'Shannon effective index', 'Simpson index', 'Simpson effective index', 'Evenness']
    
    df = pd.DataFrame(list(zip(ids, richness, shannon, shannon_effective, simpson, simpson_effective, simpson_e)),
                      columns=['SampleID'] + all_param,
                      ).set_index('SampleID')
    df.to_csv(os.path.join(outdir, 'alpha_diversity.tab'), sep='\t')      
    # Metadata
    df_metainfo = pd.read_csv(metafile, sep='t').set_index(sample)
    df['subject'] = df_metainfo[column]
    print(df_metainfo[column])
    pairs = list(combinations(df['subject'].unique(), 2))
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 8))
    fig.suptitle('Alpha diversity', fontsize=16)
    plot_loc = 231
    stats_param = dict()
    # plt.title(label='Alpha diversity')
    for i_param in range(len(all_param)):
        param = all_param[i_param]
        ax = plt.subplot(plot_loc)
        stats_param.update({param:[(i,j) for i,j in zip(pairs, compute_stat(df, param, pairs))]})
        print(df)
        boxplot(ax, df, 'subject', param, pairs)
        plot_loc += 1    
    fig.tight_layout()
    plt.savefig(os.path.join(outdir, 'alpha.png'), bbox_inches='tight', dpi=180)


# Confident ellipse covers points in pcoa
def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    print(mean_x, mean_y, scale_x, scale_y)

    transf = transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


# Compute beta diversity
def compute_beta_diversity(abundance_file, metafile, sample, column, outdir):
    abun_tab = pd.read_csv(abundance_file, sep='\t')
    abun_tab = abun_tab.drop('clade_name', axis=1)
    abun_tab = abun_tab.T
    ids = abun_tab.index.to_list()

    # Bray-Curtis
    beta_diversity = skbio.diversity.beta_diversity("braycurtis", abun_tab, ids)
    # Metadata
    df_metainfo = pd.read_csv(metafile, sep='t').set_index(sample)
    df_metainfo = df_metainfo.loc[ids,:]
    unique_grp = df_metainfo[column].unique()

    # recovery, norecovery = df_metainfo[df_metainfo[column]=='Recovery'].index.to_list(), df_metainfo[df_metainfo[column]=='No Recovery'].index.to_list()
    # PCoA
    beta_pcoa = pcoa(beta_diversity)
    coord_proportion = beta_pcoa.proportion_explained
    df_pcoa = beta_pcoa.samples[['PC1','PC2']]
    print('df_pcoa', df_pcoa)
    print('df_metainfo', df_metainfo)
    print('df_metainfo', df_metainfo.loc[df_pcoa.index, [column]])
    df_pcoa['subject'] = df_metainfo.loc[df_pcoa.index, [column]]
    fig, ax_nstd = plt.subplots(figsize=(6, 6))
    fig.suptitle('Beta diversity', fontsize=16)
    gfg = sns.scatterplot(data=df_pcoa, x="PC1", y="PC2", hue="subject")
    gfg.set(xlabel="PC1 ({}%)".format(round(coord_proportion[0]*100, 2)), ylabel="PC2 ({}%)".format(round(coord_proportion[1]*100, 2)))
    for ugrp in unique_grp:
        grp_sample = df_metainfo[df_metainfo[column] == ugrp].index.to_list()
        confidence_ellipse(df_pcoa.loc[grp_sample, "PC1"].to_numpy(), df_pcoa.loc[grp_sample, "PC2"].to_numpy(), ax_nstd, n_std=1, edgecolor='grey')
    # confidence_ellipse(df_pcoa.loc[norecovery,"PC1"].to_numpy(), df_pcoa.loc[norecovery,"PC2"].to_numpy(), ax_nstd, n_std=1,edgecolor='grey')
    results = anosim(beta_diversity, df_metainfo, column=column, permutations=999)
    print('ANOSIM p-value: ', results['test statistic'])
    plt.text(0.3, -.5, 'ANOSIM p-value: ' + str(round(results['test statistic'], 4)), rotation=0, verticalalignment='center', horizontalalignment='center', color='#000000', fontweight='normal', in_layout=True, fontsize=9)
    plt.savefig(os.path.join(outdir, 'pcoa.png'), dpi=200, bbox_inches='tight')


def run_diversity_execution(project_dir, process_dir):
    config_file = config.read_config(project_dir)

    tax_lbl_for_diversity = config.read_from_config(config_file, 'Diversity', 'tax_lbl_for_diversity')
    taxofile = '4_family.tab' if tax_lbl_for_diversity == 'f' else '5_genera.tab' if tax_lbl_for_diversity == 'g' else '6_species.tab' 
    metafile = config.read_from_config(config_file, 'Diversity', 'metafile_for_diversity')
    sample = config.read_from_config(config_file, 'Diversity', 'metafile_sampleid')
    metacol = config.read_from_config(config_file, 'Diversity', 'metafile_category')
    abund = float(config.read_from_config(config_file, 'Diversity', 'abundace_cutoff'))
    preval = float(config.read_from_config(config_file, 'Diversity', 'prevalent_cutoff'))
    
    # for non-usgb and usgb
    for category in ['ignore_usgb', 'usgb']:
        taxprof = os.path.join(project_dir, 'taxo', 'taxonomic_profile', category, 'Taxonomic_binning', taxofile)

        # Filtering based on abundace and prevalence
        output_dir = os.path.join(process_dir, 'diversity', 'filtered_taxprof', category)
        util.create_dir(output_dir)
        fitered_taxprof = os.path.join(output_dir, os.path.basename(taxprof))
        fiter_taxprof(taxprof, abund, preval, fitered_taxprof)
        # Alpha diversity
        output_dir = os.path.join(process_dir, 'diversity', 'alpha_diversity', category)
        util.create_dir(output_dir)
        compute_alpha_diversity(fitered_taxprof, metafile, sample, metacol, output_dir)
        if os.path.isfile(metafile):
            # Beta diversity
            output_dir = os.path.join(process_dir, 'diversity', 'beta_diversity', category)
            util.create_dir(output_dir)
            compute_beta_diversity(fitered_taxprof, metafile, sample, metacol, output_dir)
        else:
            print('Metafile not found. Diversity not computed')
