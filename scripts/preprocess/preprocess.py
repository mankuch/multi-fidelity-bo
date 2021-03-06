import numpy as np


def get_best_acquisition(data):
    """Returns coordinates x and f(x) for lowest observed acquisition.

    Args:
        data (dict): Parsed data from boss.out
    """
    return np.array(data['best_acq'])[-1, :]


def substract_y_offset(data):
    """Adds the offsets (= lowest observed acquisition) to the energy values.

    Args:
        data (dict): Parsed data from boss.out
    """
    y_offset = np.array(data['truemin'])[:, -1]
    for value in data['gmp']:
        value[-2] -= y_offset[0]
    for value in data['best_acq']:
        value[-1] -= y_offset[0]

    N_sources = len(y_offset)
    if N_sources == 1:                          # Baseline runs
        for value in data['xy']:
            value[-1] -= y_offset[0]
    elif N_sources > 1:                         # TL runs
        for value in data['xy']:
            for i in range(N_sources):
                if value[-2] == i:
                    value[-1] -= y_offset[i]


def add_init_acq_times(data, init_data_cost):
    """Adds computational cost for the initial acquisitions, used for
    Transfer Learning.

    data['initpts'] contains a list with the
    number of initial points for each fidelity. E.g. [2, 0].

    Args:
        data (dict): Parsed data from boss.out
        init_data_cost (list): List containing the additional acquisition
        times from the initialization data.
    """
    accounted_initpts = 0
    for cost, initpts in zip(init_data_cost, data['initpts']):
        # init strategy 'self'
        if cost is None:
            pass
        # init data is taken from baseline
        else:
            begin = accounted_initpts
            if accounted_initpts != 0:
                begin -= 1
            end = begin + initpts
            for i in range(begin, end):
                data['total_time'][i] += cost[i-begin]
            for i in range(end, len(data['total_time'])):
                data['total_time'][i] += cost[initpts-1]
        accounted_initpts += initpts


def calculate_convergence_times(data, idx, measure='gmp'):
    """Calculates the convergence points/times of a quantity for given
    tolerances.

    Args:
        data (dict): Cotanins the parsed data.
        idx (int): Dimension where data is located (has to be taken
        into account for MT runs).
        measure (str, optional): Quantity to calculate convergence measures
        for. Defaults to 'gmp'.
    """
    if data[measure] == []:
        return          # This is for interrupted sobol runs (hardcoded fix)
    values = np.atleast_2d(data[measure])[:, idx][::-1]     # note reversion
    data[f'iterations_to_{measure}_convergence'] = []       # BO iterations
    data[f'totaltime_to_{measure}_convergence'] = []        # total runtime
    data[f'observations_to_{measure}_convergence'] = []     # BO + init points

    for tolerance in data['tolerance_levels']:
        i = 0
        for value in values:
            if abs(value) > tolerance:
                break
            i += 1
        if i == 0:
            iterations = None
            totaltime = None
            observations = None
        else:
            iterations = len(values) - i
            totaltime = data['total_time'][-i]
            observations = len(data['xy']) - i
        data[f'iterations_to_{measure}_convergence'].append(iterations)
        data[f'totaltime_to_{measure}_convergence'].append(totaltime)
        data[f'observations_to_{measure}_convergence'].append(observations)

    if 'ICM' in data['name']:
        data[f'highest_fidelity_iterations_to_{measure}_convergence'] = []
        for tolerance in data['tolerance_levels']:
            i = 0
            for value in values:
                if abs(value) > tolerance:
                    break
                i += 1
            if i == 0:
                iterations = None
            else:
                iterations = data['highest_fidelity_iterations'][-i]
            data[f'highest_fidelity_iterations_to_{measure}_convergence'].\
                append(iterations)
    else:
        data[f'highest_fidelity_iterations_to_{measure}_convergence'] = \
            data[f'iterations_to_{measure}_convergence']



def calculate_B(data):
    dim = data['dim']
    if dim == len(data['xy'][0])-1:
        data['B'] = None
    else:
        data['B'] = []
        tasks = data['tasks']
        for params in data['GP_hyperparam']:
            W = np.array(params[dim:-tasks]).reshape((-1, tasks))
            Kappa = np.diag(params[-tasks:])
            B = W.dot(W.T) + Kappa
            data['B'].append([b for b in B.flatten()])


def preprocess(data, tolerance_levels=[0], init_data_cost=None):
    """Adds time taken for initialization data (acquisition time). #
    Calculates model time.
    Rescales output so that best acquisition of the baseline experiment is 0.
    Calculates convergence.


    Args:
        data (dict): Dict containing the data of boss.out
        tolerance_levels (list, optional): List of tolerance levels.
        Defaults to [0].
        init_data_cost (float, optional): Cost of the initial data.
        Defaults to None.
    """
    # Add times for the GPR model
    data['model_time'] = [iter_time-acq_time for iter_time, acq_time in
                          zip(data['iter_times'][::-1],
                              data['acq_times'][::-1])]
    data['model_time'] = data['model_time'][::-1]

    # Adds (possible) extra cost for initialization data
    if init_data_cost is not None:
        add_init_acq_times(data, init_data_cost)

    # Add offset to the data and add convergence times
    substract_y_offset(data)
    data['tolerance_levels'] = tolerance_levels
    calculate_convergence_times(data, idx=-2)

    calculate_B(data)

    return data

def get_highest_fidelity_iterations(data):
    flag_highest_fidelity_samples = []
    for sample_idx in data['sample_indices']:
        if sample_idx == 0:
            flag_highest_fidelity_samples.append(1)
        else:
            flag_highest_fidelity_samples.append(0)
    return np.cumsum(flag_highest_fidelity_samples).tolist()
