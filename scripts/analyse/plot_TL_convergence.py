import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
# import pylustrator
# pylustrator.start()

import read_write


THESIS_DIR = Path(__name__).resolve().parent.parent.parent
FIGS_DIR = THESIS_DIR / 'results/figs'
TL_CONFIG = read_write.load_yaml(THESIS_DIR / 'scripts/analyse/config',
                              '/transfer_learning.yaml')
tl_experiments = [THESIS_DIR / 'data' / 'processed' /
                  exp for exp in TL_CONFIG.keys()]
# baselines, corresponding to each tl experiment
baseline_experiments = [THESIS_DIR / 'data' / 'processed' /
                  TL_CONFIG[exp][0] for exp in TL_CONFIG]

SCATTER_DICT = {'color': 'blue', 'alpha': .4, 'marker': 'x',
                'label': 'observation'}
FIT_DICT = {'color': 'red', 'label': 'trend', 'linewidth': 3,
            'linestyle': 'dashed', 'alpha': .5}
MEANS_DICT = {'color': 'red', 'marker': '*', 's': 100}


def main():
    tl_experiment_data = load_experiments(tl_experiments)
    baseline_experiment_data = load_experiments(baseline_experiments)
    plot_tl_convergence('2DUHF.pdf',
                        baseline_experiment_data, tl_experiment_data)


def load_experiments(experiments):
    experiments_data = []
    for experiment in experiments:
        exp_data = []
        for exp in experiment.iterdir():
            if exp.is_file():
                exp_data.append(read_write.load_json('', exp))
        experiments_data.append(exp_data)
    return experiments_data


def plot_tl_convergence(figname, baseline_experiments, tl_experiments):
    N = len(tl_experiments)
    fig, axs = plt.subplots(2, N, figsize=(5*N, 10), sharey='row')

    SMALL_SIZE = 15
    MEDIUM_SIZE = 20
    LARGE_SIZE = 25

    for tl_exp_idx in range(N):
        baseline_data = baseline_experiments[tl_exp_idx]
        tl_data = tl_experiments[tl_exp_idx]

        explist = baseline_data
        for tl_exp in tl_data:
            explist.append(tl_exp)

        convergence_iterations, convergence_times = [], []
        for exp in explist:
            if len(exp['initpts']) > 1:
                secondary_initpts = int(exp['initpts'][1])
            else:
                secondary_initpts = 0
            convergence_iter = exp['iterations_to_gmp_convergence'][5]
            convergence_iterations.append([secondary_initpts,
                                           convergence_iter])

            convergence_time = exp['totaltime_to_gmp_convergence'][5]
            convergence_times.append([secondary_initpts,
                                      convergence_time])

        for quantity_idx, quantity in enumerate([convergence_iterations,
                                                 convergence_times]):
            # scatter
            quantity = np.array(quantity, dtype=float)
            axs[quantity_idx, tl_exp_idx].scatter(quantity[:, 0],
                                                  quantity[:, 1],
                                                  **SCATTER_DICT)
            # fit
            x = quantity[:, 0].reshape(-1, 1)
            y = quantity[:, 1].reshape(-1, 1)
            reg = LinearRegression().fit(x, y)
            x_plot = np.arange(0, 50, 0.01).reshape(-1, 1)
            y_plot = reg.predict(x_plot)
            axs[quantity_idx, tl_exp_idx].plot(x_plot, y_plot, **FIT_DICT)
            # means
            for initpts_idx, initpts in enumerate(np.unique(x)):
                mean = np.mean(y[x == initpts])
                if initpts_idx == 0:
                    axs[quantity_idx, tl_exp_idx].scatter(
                        [initpts], [mean], **MEANS_DICT, label='mean')
                else:
                    axs[quantity_idx, tl_exp_idx].scatter(
                        [initpts], [mean], **MEANS_DICT)
            axs[0, 0].legend(fontsize=SMALL_SIZE)
        #title = f'{i+1}a) {expname}'
        #axs[0,i].set_title(title, loc='left', fontsize=SMALL_SIZE)
        # title = f'{i+1}b) {expname}'
        # axs[1,i].set_title(title, loc='left', fontsize=SMALL_SIZE)
    axs[0, 0].set_xticks([])
    axs[0, 1].set_xticks([])
    axs[1, 0].set_yticks([0, 50000, 100000, 150000, 200000, 250000, 300000])
    axs[1, 0].set_xticks([0, 25, 50])
    axs[1, 1].set_xticks([0, 25, 50])
    axs[0, 0].set_ylabel('BO iterations',
                        fontsize=SMALL_SIZE)
    axs[1,0].set_ylabel('CPU time [s]', fontsize=SMALL_SIZE)
    for ax in axs[1, :]:
        ax.set_xlabel('secondary initpts', fontsize=SMALL_SIZE)

    # for ax in axs.flatten():
    #     # ax.spines['bottom'].set_visible(False)
    #     # ax.spines['left'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.spines['top'].set_visible(False)

    fig.suptitle('2UHF - BO iterations and CPU times to GMP convergence',
                 fontsize=MEDIUM_SIZE)
    plt.tight_layout()
    #% start: automatic generated code from pylustrator
    plt.figure(1).ax_dict = {ax.get_label(): ax for ax in plt.figure(1).axes}
    import matplotlib as mpl
    plt.figure(1).axes[0].legend(frameon=False, fontsize=12, title_fontsize=10.0)
    plt.figure(1).axes[0].set_position([0.102903, 0.513069, 0.431118, 0.428931])
    plt.figure(1).axes[0].get_legend()._set_loc((0.033231, 0.041998))
    plt.figure(1).axes[0].get_legend()._set_loc((0.072663, 0.048992))
    plt.figure(1).axes[0].get_legend()._set_loc((0.065705, 0.055986))
    plt.figure(1).axes[1].set_position([0.553882, 0.513069, 0.431118, 0.428931])
    plt.figure(1).text(0.5, 0.5, 'New Text', transform=plt.figure(1).transFigure)  # id=plt.figure(1).texts[1].new
    plt.figure(1).texts[1].set_fontsize(16)
    plt.figure(1).texts[1].set_position([0.440000, 0.912000])
    plt.figure(1).texts[1].set_text("(a) LF")
    plt.figure(1).texts[1].set_weight("bold")
    plt.figure(1).text(0.5, 0.5, 'New Text', transform=plt.figure(1).transFigure)  # id=plt.figure(1).texts[2].new
    plt.figure(1).texts[2].set_fontsize(16)
    plt.figure(1).texts[2].set_position([0.887000, 0.912000])
    plt.figure(1).texts[2].set_text("(c) HF")
    plt.figure(1).texts[2].set_weight("bold")
    plt.figure(1).text(0.5, 0.5, 'New Text', transform=plt.figure(1).transFigure)  # id=plt.figure(1).texts[3].new
    plt.figure(1).texts[3].set_fontsize(16)
    plt.figure(1).texts[3].set_position([0.440000, 0.458000])
    plt.figure(1).texts[3].set_text("(b) LF")
    plt.figure(1).texts[3].set_weight("bold")
    plt.figure(1).text(0.5, 0.5, 'New Text', transform=plt.figure(1).transFigure)  # id=plt.figure(1).texts[4].new
    plt.figure(1).texts[4].set_fontsize(16)
    plt.figure(1).texts[4].set_position([0.887000, 0.458000])
    plt.figure(1).texts[4].set_text("(d) HF")
    plt.figure(1).texts[4].set_weight("bold")
    #% end: automatic generated code from pylustrator
    plt.show()
    #plt.savefig(FIGS_DIR.joinpath(figname), dpi=300)


main()