from pathlib import Path
from src.read_write import load_yaml, load_experiments, \
    load_statistics_to_dataframe
from posixpath import split
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
plt.rcParams.update({"text.usetex": True, "font.size": 12})  # Tex rendering
import seaborn as sns
import pandas as pd
import click


THESIS_DIR = Path(__file__).resolve().parent.parent.parent
FIGS_DIR = THESIS_DIR / 'results/figs'
CONFIG = load_yaml(THESIS_DIR / 'scripts', '/config_mt.yaml')


@click.command()
@click.option('--show_plots', default=False, is_flag=True,
              help='Show (and don\'t save) plots.')
@click.option('--dimension', default='2D', type=str,
              help='Chose between 2D or 4D.')
@click.option('--tolerance', default=0.23, type=float,
              help='Tolerance level to plot convergence for.')
@click.option('--highest_fidelity', default='uhf', type=str,
              help="Chose between 'uhf' and 'hf'.")
@click.option('--print_non_converged', default=False, is_flag=True,
              help='Print a sub-dataframe of unconverged runs')
@click.option('--print_summary', default=False, is_flag=True,
              help='Print summary statistics of the dataframe to the terminal')
def main(show_plots, dimension, tolerance, highest_fidelity,
         print_non_converged, print_summary):
    tolerances = np.array(CONFIG['tolerances'])
    if tolerance not in tolerances:
        raise Exception(f"Invalid tolerance level, chose from {tolerances}")
    #config = CONFIG[f'TL_experiment_plots_{dimension}']
    config = CONFIG[f'MT_experiment_plots_{dimension}']

    tl_experiments = [THESIS_DIR / 'data/multi_task_learning' / 'processed' /
                      exp for exp in config.keys()]

    # Don't load baseline experiments multiple times
    bl_experiment_keys = list(set([config[exp][0] for exp in config]))
    bl_experiments = [THESIS_DIR / 'data/multi_task_learning' / 'processed' /
                      exp for exp in bl_experiment_keys]
    tl_exp_data = load_experiments(tl_experiments)
    bl_exp_data = load_experiments(bl_experiments)
    df = load_statistics_to_dataframe(bl_exp_data, tl_exp_data, num_exp=5)
#    df.to_csv('mt_test.csv')
    plot_convergence_as_boxplot(
        df, tolerance, dimension, highest_fidelity, show_plots,
        print_non_converged, print_summary)


def plot_convergence_as_boxplot(
        df, tolerance, dimension, highest_fidelity, show_plots,
        print_not_converged, print_summary):
    tolerance_idx = np.argwhere(
        tolerance == np.array(np.array(CONFIG['tolerances']))).squeeze()

    plot_df = df[['name', 'iterations_to_gmp_convergence',
                  'totaltime_to_gmp_convergence',
                  'highest_fidelity_iterations_to_gmp_convergence']]

    plot_df['iterations'] = plot_df[
        'iterations_to_gmp_convergence'].map(lambda x: x[tolerance_idx])
    plot_df['Highest fidelity\niterations'] = plot_df[
        'highest_fidelity_iterations_to_gmp_convergence'].map(
            lambda x: x[tolerance_idx])
    plot_df
    plot_df['CPU time [h]'] = plot_df[
        'totaltime_to_gmp_convergence'].map(
            lambda x: chose_value_with_tolerance(x, tolerance_idx))

    if highest_fidelity == 'uhf':
        plot_df = plot_df[plot_df['name'].str.contains('UHF') == True]
    elif highest_fidelity == 'hf':
        plot_df = plot_df[plot_df['name'].str.contains('UHF') == False]
    else:
        raise Exception("Invalid highest fidelity")

    fig, axs = plt.subplots(2, 1, figsize=(6.5, 5.5))
    conditions_strategy = [
        (plot_df['name'].str.contains('basic') ),
        (plot_df['name'].str.contains('ICM1')),
        (plot_df['name'].str.contains('ICM2'))]
    strategies = ['Baseline', r'LF $\rightarrow$ UHF',
                  r'HF $\rightarrow$ UHF']
    conditions_approach = [
        (plot_df['name'].str.contains('basic')),
        (plot_df['name'].str.contains('ELCB1')),
        (plot_df['name'].str.contains('ELCB3')),
        (plot_df['name'].str.contains('ELCB6'))]
    approaches = ['Single fidelity', 'MFBO approach 1',
                  'MFBO approach 3',
                  'MFBO approach 6']
    if print_not_converged:
        iterations_df = plot_df[['name', 'iterations']]
        print(iterations_df[iterations_df['iterations'].isna()])
    plot_df['Setup'] = np.select(conditions_strategy, strategies)
    plot_df['Strategy'] = np.select(conditions_approach, approaches)
    if print_summary:
        print(plot_df.groupby(['Setup', 'Strategy'])\
            ['CPU time [h]'].describe(percentiles=[.5]).round(2))
    sns.boxplot(x='Setup', y='Highest fidelity\niterations', hue='Strategy',
                whis=[0.25, 0.75], data=plot_df, palette="tab10", ax=axs[0])
    sns.boxplot(x='Setup', y='CPU time [h]', hue='Strategy', whis=[0.25, 0.75],
                data=plot_df, palette="tab10", ax=axs[1])
    fig.suptitle(
        f'{dimension} Multi-task learning convergence results', fontsize=16)
    fig.tight_layout()

    if show_plots:
        plt.show()
    else:
        name = f'MT_convergence_boxplot_{dimension}_{highest_fidelity}'
        plt.savefig(FIGS_DIR / f'{name}.pdf')


def chose_value_with_tolerance(x, tolerance_idx, time_in_h=True):
    if x[tolerance_idx] is None:
        return None
    else:
        x_tol = x[tolerance_idx] / 3600 if time_in_h else x[tolerance_idx]
        return x_tol

if __name__ == '__main__':
    main()