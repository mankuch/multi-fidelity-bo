import numpy as np
import matplotlib.pyplot as plt
#import pylustrator
# plt.switch_backend('agg')
from pathlib import Path

import read_write


class recreate_settings_format:
    def __init__(self, data):
        self.dim = data['settings']['dim']
        self.pp_m_slice = data['settings']['pp_m_slice']
        self.bounds = np.array(data['settings']['bounds'])


def main():
    data = read_write.load_json(Path(__file__).resolve().parent,
                                '/raw_data_for_plot_100.json')
    data['STS'] = recreate_settings_format(data)
    del data['settings']
    data['model_data'] = np.array(data['model_data'])
    data['xhat'] = np.array(data['xhat'])
    data['acqs'] = np.array(data['acqs'])
    data['xnext'] = np.array(data['xnext'])
    model(**data)
#    dest_file = 'test'
#    model_data = data['model_data']


def model(STS, dest_file, model_data, xhat=None, acqs=None, xnext=None,
                minima=None, truef=None, incl_uncert=True,
                axis_labels=None, legends=True, paths=None):
    """
    Plots a (max 2D) slice of the model.
    """
    acqs, xnext = None, None
    legends = False
#    pylustrator.start()
    coords = model_data[:,:STS.dim]
    mu, nu = model_data[:,-2], model_data[:,-1]
    slice_dim = 1 if STS.pp_m_slice[0] == STS.pp_m_slice[1] else 2
    if axis_labels is None:
        axis_labels = ["$x_%i$"%(STS.pp_m_slice[0]+1), "$x_%i$"%(STS.pp_m_slice[1]+1)]

    if slice_dim == 1:
        x1 = coords[:,STS.pp_m_slice[0]]
        if truef is not None:
            crds = truef[:,:STS.dim]
            tf = truef[:,-1]
            tfx1 = crds[:,STS.pp_m_slice[0]]
            plt.plot(tfx1, tf, 'k', linewidth=5, label='f(x)')
        if incl_uncert:
            plt.fill_between(x1, mu + nu, mu, color='lightgrey')
            plt.fill_between(x1, mu - nu, mu, color='lightgrey')
            plt.plot(x1, mu + nu, 'grey', linewidth=3, label='$\\nu(x)$')
            plt.plot(x1, mu - nu, 'grey', linewidth=3)
        plt.plot(x1, mu, 'b', linewidth=5, label='$\\mu(x)$')

        if xhat is not None:
            plt.axvline(xhat[STS.pp_m_slice[0]], color='red', linewidth=5,
                            label='$\hat{x}$', zorder=19)

        if acqs is not None:
            x1 = acqs[:,STS.pp_m_slice[0]]; y = acqs[:,-1];
            plt.scatter(x1, y, s=200, linewidth=6, facecolors='none',
                            edgecolors='brown', label='acqs', zorder=18)

        if xnext is not None:
            plt.axvline(xnext[STS.pp_m_slice[0]], color='green', linewidth=5,
                    label='$x_{next}$', linestyle='dashed', zorder=20)

        if minima is not None:
            x1 = minima[:,STS.pp_m_slice[0]]; y = minima[:,-2];
            plt.scatter(x1, y, s=250, linewidth=6, zorder=19,
                        facecolors='none', edgecolors='lawngreen',
                        label='minima')

        plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
        yd = max(mu) - min(mu)
        plt.ylim(min(mu) - 0.1*yd, max(mu) + 0.1*yd)
        plt.xlabel(axis_labels[0], size=24)
        plt.ylabel('$y$', size=24)
        if legends:
            lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                ncol=4, mode="expand", borderaxespad=0.,
                                prop={'size':20})
        plt.gcf().set_size_inches(10, 8)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        #plt.tight_layout()
        if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,),
            bbox_inches='tight')
        else:
            plt.savefig(dest_file)
        plt.close()

    elif slice_dim == 2:
        npts = STS.pp_m_slice[2]
        x1 = coords[:,STS.pp_m_slice[0]]
        x2 = coords[:,STS.pp_m_slice[1]]

        if truef is not None:
            pass # 2D true func slice will be plotted in separate graph only

        if incl_uncert:
            plt.contour(x1[:npts], x2[::npts], nu.reshape(npts,npts),
                            10, colors = 'k')
            plt.contourf(x1[:npts], x2[::npts], nu.reshape(npts,npts),
                            7, cmap='viridis')
            cbar = plt.colorbar()#, orientation='horizontal')
            cbar.set_label(label='$\\nu(x)$', size=24)
            cbar.ax.tick_params(labelsize=18)
            plt.xlabel(axis_labels[0], size=24)
            plt.ylabel(axis_labels[1], size=24)
            plt.gcf().set_size_inches(10, 8)
            plt.gca().tick_params(labelsize=18)
            plt.tight_layout()
            plt.savefig(dest_file[:-4] + '_uncert.pdf')
            plt.close()

        plt.contour(x1[:npts], x2[::npts], mu.reshape(npts,npts),
                        25, colors = 'k')
        plt.contourf(x1[:npts], x2[::npts], mu.reshape(npts,npts),
                        5, cmap='inferno') # this value is usually fixed at 150
        cbar = plt.colorbar()#, orientation='horizontal')
        cbar.set_label(label='$\mu(x)$', size=24)
        cbar.ax.tick_params(labelsize=18)

        lo = False
        if xhat is not None:
            plt.plot(xhat[STS.pp_m_slice[0]], xhat[STS.pp_m_slice[1]], 'r*',
            markersize=26, zorder=21, label='$\hat{x}$')
            lo = True

        if acqs is not None:
            x1 = acqs[:,STS.pp_m_slice[0]]; x2 = acqs[:,STS.pp_m_slice[1]];
            sz = np.linspace(200,500,len(x1))
            lw = np.linspace(3,8,len(x1))
            plt.scatter(x1[0], x2[0], s=sz[int(len(x1)/2.)],
                linewidth=lw[int(len(x1)/2.)], zorder=10, facecolors='none',
                edgecolors='green', label='acqs')
            for i in range(len(x1)):
                plt.scatter(x1[i], x2[i], s=sz[i], linewidth=lw[i],
                    zorder=10, facecolors='none', edgecolors='green')
            lo = True

        if xnext is not None:
           plt.plot(xnext[STS.pp_m_slice[0]], xnext[STS.pp_m_slice[1]], 'b^',
                           markersize=26, label='$x_{next}$', zorder=20)
           lo = True

        if minima is not None:
            x1 = minima[:,STS.pp_m_slice[0]]; x2 = minima[:,STS.pp_m_slice[1]];
            plt.scatter(x1, x2, s=350, linewidth=6, facecolors='none',
                        edgecolors='navajowhite', zorder=11, label='minima')
            lo = True

        if paths is not None:
            threshold = min(STS.bounds[:,1] - STS.bounds[:,0]) / 2
            for path in paths:
                start = 0
                stop = 1
                while True:
                    if (stop == path.crds.shape[0]-1 or
                            np.linalg.norm(path.crds[stop,:]
                            - path.crds[stop-1,:]) > threshold):
                        plt.plot(path.crds[range(start, stop),0],
                                    path.crds[range(start, stop),1],
                                    linewidth=3.0,
                                    color='red',
                        )
                        if stop == path.crds.shape[0]-1: break
                        else: start = stop
                    stop += 1

        plt.xlim(min(coords[:,STS.pp_m_slice[0]]), max(coords[:,STS.pp_m_slice[0]]))
        plt.ylim(min(coords[:,STS.pp_m_slice[1]]), max(coords[:,STS.pp_m_slice[1]]))
        plt.xlabel(axis_labels[0], size=24)
        plt.ylabel(axis_labels[1], size=24)
        top = 0.99
        if legends and lo:
            lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                                ncol=4, mode="expand", borderaxespad=0.,
                                prop={'size':20})
            top = 0.85
        plt.gcf().set_size_inches(10, 8)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        #plt.tight_layout()


        if legends: # FOR OLD MATPLOTLIB COMPATIBILITY
            # #% start: automatic generated code from pylustrator
            # plt.figure(1).ax_dict = {ax.get_label(): ax for ax in plt.figure(1).axes}
            # import matplotlib as mpl
            # plt.figure(1).ax_dict["<colorbar>"].yaxis.labelpad = -45.760000
            # plt.figure(1).ax_dict["<colorbar>"].get_yaxis().get_label().set_rotation(0.0)
            # plt.figure(1).axes[0].legend(frameon=False, ncol=4, fontsize=20.0, title_fontsize=10.0)
            # plt.figure(1).axes[0].get_legend()._set_loc((-0.012903, 0.097922))
            # plt.figure(1).axes[0].get_legend()._set_loc((0.095161, 1.017001))
            # plt.figure(1).axes[0].get_xaxis().get_label().set_text("$d_{4}$")
            # plt.figure(1).axes[0].get_yaxis().get_label().set_text("$d_{13}$")
            # #% end: automatic generated code from pylustrator
#            plt.show()
            plt.tight_layout()
            plt.savefig(dest_file, bbox_extra_artists=(lgd,),
            bbox_inches='tight')
        else:
            #plt.show()
            plt.tight_layout()
            plt.savefig(dest_file)
        plt.close()
    else:
        raise TypeError("ERROR: Model plot only applicable up to 2D (slices)")

main()
