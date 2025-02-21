#!/user/bin/env python3

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

import util, config


def merging_abundance(output_dir, sampleseq):
    tax_file = os.path.join(output_dir, 'OTUtable.rel_abundance.tab')
    filelist = ''
    for s in sampleseq:
        filelist += os.path.join(output_dir, 'profiles', s + '.txt') + ' '
    cmd = 'merge_metaphlan_tables.py ' + filelist + ' > ' + tax_file
    os.system(cmd)
    df_merged = pd.read_csv(tax_file, sep='\t', comment="#")
    df_merged = df_merged.set_index('clade_name')[sampleseq]
    df_merged.to_csv(tax_file, sep='\t')
    return tax_file


def separate_taxrank(output_dir, merged_file):
    outdir = os.path.join(output_dir, 'Taxonomic_binning')
    util.create_dir(outdir)
    
    fp_k = open(outdir + '/0_kingdom.tab', 'w')
    fp_p = open(outdir + '/1_phylum.tab', 'w')
    fp_c = open(outdir + '/2_class.tab', 'w')
    fp_o = open(outdir + '/3_order.tab', 'w')
    fp_f = open(outdir + '/4_family.tab', 'w')
    fp_g = open(outdir + '/5_genera.tab', 'w')
    fp_s = open(outdir + '/6_species.tab', 'w')
    # fp_t = open(outdir+'/7_strain.tab', 'w')

    fp = open(merged_file, 'r')
    # line = fp.readline()
    line = fp.readline()
    fp_k.write(line)
    fp_p.write(line)
    fp_c.write(line)
    fp_o.write(line)
    fp_f.write(line)
    fp_g.write(line)
    fp_s.write(line)
    # fp_t.write(line)

    while True:
        line = fp.readline()
        if line:
            # tax = line.split('\t')[0].split('|')[-1]
            tax = line.split('|')[-1]
            if 'k__' in tax:
                fp_k.write(tax)
            elif 'p__' in tax:
                fp_p.write(tax)
            elif 'c__' in tax:
                fp_c.write(tax)
            elif 'o__' in tax:
                fp_o.write(tax)
            elif 'f__' in tax:
                fp_f.write(tax)
            elif 'g__' in tax:
                fp_g.write(tax)
            elif 's__' in tax:
                fp_s.write(tax)
            # elif 't__' in tax:
            #     fp_t.write(tax)
        else:
            fp.close()
            fp_k.close()
            fp_p.close()
            fp_c.close()
            fp_o.close()
            fp_f.close()
            fp_g.close()
            fp_s.close()
            # fp_t.close()
            break
    return outdir


def plot_relabundance(abun_file, show_top_n, show_abundant, metadata):
    # 10 colors
    # colors= ['#EE9B01','#68904D','#FAD074','#3582b9','#ebf02c','#BC8848','#f5ebff','#3ae5e5','#511970','#85c3fe']
    # 20 colors
    colors= ['#3eb489','#ff6ec7','#ffd12b','#03324a','#16621c','#5f2e4c','#f9584b','#596fff','#81dd4d','#e6b710',
             '#ff8980','#00FFFD','#b5db52','#FF6900','#c90076','#2ffd51','#ff8933','#EE9B01','#68904D','#FAD074',
             '#3582b9','#ebf02c','#BC8848','#f5ebff','#3ae5e5','#511970','#85c3fe']
    abun_tab = pd.read_table(abun_file, sep='\t')
    abun_tab = abun_tab.set_index('clade_name')
    abun_tab['avg'] = abun_tab.mean(axis='columns')
    abun_tab = abun_tab.sort_values('avg', ascending=False)
    high_abund = abun_tab[abun_tab['avg'] > show_abundant].index.to_list()
    top = abun_tab.nlargest(show_top_n, 'avg').index.to_list()
    show_taxa = list(set(high_abund).intersection(set(top)))
    df1 = abun_tab.loc[show_taxa].sort_values(by=show_taxa, ascending=[True] * len(show_taxa), axis=1)
    df1.loc['others'] = abun_tab.loc[list(set(abun_tab.index.to_list()).difference(show_taxa)),:].sum(axis='index').to_list()
    df1 = df1.drop(columns='avg')
    df1 = df1.T

    if isinstance(metadata, str):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax = df1.plot(kind='bar', stacked=True,
                      color=colors[:df1.shape[1]-1]+['#cccccc'],
                      legend='reverse', figsize=(130, 50), grid=True, width=0.8)
        ax.grid(axis='x')
        ax.set_xticklabels(labels=df1.index.to_list(), fontsize=60, rotation=90)
        label_format = '{:.0f}'
        ticks_loc = ax.get_yticks().tolist()
        ax.set_yticks(ax.get_yticks().tolist())
        ax.set_yticklabels([label_format.format(x) for x in ticks_loc], fontsize=60)
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), title='', fontsize="80")
    else:
        group = metadata.unique()
        fig, axes = plt.subplots(nrows=1, ncols=len(group))
        ax_position = 0
        # sns.set_style("whitegrid")
        for grp in group:
            subset = df1.loc[metadata[metadata == grp].index.to_list(),:]
            ax = subset.plot(kind='bar', stacked=True,
                             color=colors[:subset.shape[1]-1]+['#cccccc'],
                             legend='reverse', figsize=(130, 50), grid=True, width=0.8, ax=axes[ax_position])
            ax.set_title(grp, fontsize=80, alpha=1.0)
            ax.grid(axis='x')
            ax.set_xticklabels(labels=subset.index.to_list(), fontsize=60, rotation=90)
            label_format = '{:.0f}'
            ticks_loc = ax.get_yticks().tolist()
            ax.set_yticks(ax.get_yticks().tolist())
            ax.set_yticklabels([label_format.format(x) for x in ticks_loc],fontsize=60)
            # ax.set_yticklabels(labels=[0,20,40,60,80,100],fontsize=60)
            # handles, labels = ax.get_legend_handles_labels()
            ax_position += 1
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), title='', fontsize="80")
        plt.tight_layout(pad=0., w_pad=-10, h_pad=0.0)
        for i in range(len(group)-1):
            axes[i+1].set_ylabel("")
            axes[i+1].set_yticklabels("")
            axes[i].legend().set_visible(False)        
    plt.savefig(abun_file.replace('.tab','.png'),bbox_inches='tight')


def taxoprof_stats(config_file, project_dir, process_dir):
    metafile = config.read_from_config(config_file, 'Diversity', 'metafile_for_diversity')
    sampleid = config.read_from_config(config_file, 'Diversity', 'metafile_sampleid')
    column_name = config.read_from_config(config_file, 'Diversity', 'metafile_category')
    sampleseq = pd.read_csv(os.path.join(project_dir, 'qc', 'quality_control', 'samples_to_process.tab'), sep='\t')['SampleID'].to_list()

    # for non-usgb and usgb
    for category in ['ignore_usgb','usgb']:
        output_dir = os.path.join(process_dir, 'taxonomic_profile', category)
        tax_file = merging_abundance(output_dir, sampleseq)
        tax_bining = separate_taxrank(output_dir, tax_file)

        if os.path.isfile(metafile):  
            metadata = pd.read_csv(metafile,sep='\t',index_col=sampleid).loc[sampleseq,column_name]
        else:
            metadata = 'no_metadata'
        
        for f in os.listdir(tax_bining):
            if f.endswith('.tab'):
                filename = os.path.join(tax_bining,f)
                print(filename)
                show_top_n = 20     # Show top N taxa
                show_abundant = 1      # Show the taxa with more abundance
                plot_relabundance(filename, show_top_n, show_abundant, metadata)
