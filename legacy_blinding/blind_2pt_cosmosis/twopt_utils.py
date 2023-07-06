import numpy as np

def spectrum_array_from_block(block, section_name, types, xlabel='theta', bin_format='bin_{0}_{1}'):
    is_auto = (types[0] == types[1])
    nbin_a = block[section_name, "nbin"] if block.has_value(section_name, "nbin") else block[section_name, "nbin_a"]
    nbin_b = nbin_a if is_auto else block[section_name, "nbin_b"]

    theory_angle = block[section_name, xlabel]
    n_angle = len(theory_angle)
    is_binavg = block[section_name, "bin_avg"]

    if is_binavg:
        theory_angle_edges = block[section_name, xlabel + '_edges']

    value = []
    bin1 = []
    bin2 = []
    angles = []
    angle_mins = []
    angle_maxs = [] if is_binavg else None

    for i in range(nbin_a):
        jmax = i + 1 if is_auto else nbin_b
        for j in range(jmax):
            binlabel = bin_format.format(i + 1, j + 1)
            if block.has_value(section_name, binlabel):
                cl = block[section_name, binlabel]
                bin1.extend([i + 1] * n_angle)
                bin2.extend([j + 1] * n_angle)
                angles.extend(theory_angle)
                if is_binavg:
                    angle_mins.extend(theory_angle_edges[:-1])
                    angle_maxs.extend(theory_angle_edges[1:])
                value.extend(cl)
                if is_auto and i != j:
                    bin1.extend([j + 1] * n_angle)
                    bin2.extend([i + 1] * n_angle)
                    value.extend(cl)
                    angles.extend(theory_angle)
                    if is_binavg:
                        angle_mins.extend(theory_angle_edges[:-1])
                        angle_maxs.extend(theory_angle_edges[1:])

    value = np.array(value)
    bin1 = np.array(bin1)
    bin2 = np.array(bin2)
    bins = (bin1, bin2)
    angles = np.array(angles)
    angle_mins = np.array(angle_mins) if is_binavg else None
    angle_maxs = np.array(angle_maxs) if is_binavg else None

    return angles, value, bins, is_binavg, angle_mins, angle_maxs

def spectrum_array_from_block_old(block, section_name, types, xlabel='theta', bin_format = 'bin_{0}_{1}'):
    """
    >> Updated 4/21/20 to work with bin averaging implemented for DES Y3
    
    Initially adapting this from save_2pt.py and 2pt_like code.

    No scale cutting implemented or angular sampling;
    that will be handled later. Since we
    track bin numbers and angle values, which will be checked against
    the unblinded fits file in get_dictdat_tomatch_fitsdat.
    """
    if xlabel=='theta':
        is_binavg = block[section_name,"bin_avg"]
    else:
        is_binavg = False #no bin averaging in fourier space

    # for cross correlations we must save bin_ji as well as bin_ij.
    # but not for auto-correlations.
    is_auto = (types[0] == types[1])
    if block.has_value(section_name, "nbin"):
        nbin_a = block[section_name, "nbin"]
    else:
        nbin_a = block[section_name, "nbin_a"]
        nbin_b = block[section_name, "nbin_b"]


    #This is the ell/theta values that have been calculated by cosmosis,
    # if bin averaging, these should match what's in the fits files (up to rounding)
    # if interpolating, angles will be more densely sampled than values in fits files.
    theory_angle = block[section_name,xlabel]
    n_angle = len(theory_angle) #whatevers in the block, length of array
    if is_binavg:
        theory_angle_edges = block[section_name,xlabel+'_edges'] #angle bin edges

    #The fits format stores all the measurements
    #as one long vector.  So we build that up here from the various
    #bins that we will load in.  These are the different columns
    value = []
    bin1 = []
    bin2 = []
    angles = []
    # these will only be used if averaging over angular bins
    angle_mins = []
    angle_maxs = []

    # n.b. don't have suffix option implemented here

    #Bin pairs. Varies depending on auto-correlation
    for i in range(nbin_a):
        if is_auto:
            jmax = i+1
        else:
            jmax = nbin_b
        for j in range(jmax):
            #Load and interpolate from the block
            binlabel = bin_format.format(i+1,j+1)
            if block.has_value(section_name, binlabel):
                cl = block[section_name, binlabel]
                bin1.append(np.repeat(i + 1, n_angle))
                bin2.append(np.repeat(j + 1, n_angle))
                angles.append(theory_angle)
                if is_binavg:
                    angle_mins.append(theory_angle_edges[:-1])
                    angle_maxs.append(theory_angle_edges[1:])
                value.append(cl)

                if is_auto and i!=j: #also store under flipped z bin labels
                    # this allows the script to work w fits files uing either convention
                    bin1.append(np.repeat(j + 1, n_angle))
                    bin2.append(np.repeat(i + 1, n_angle))
                    value.append(cl)
                    angles.append(theory_angle)
                    if is_binavg:
                        angle_mins.append(theory_angle_edges[:-1])
                        angle_maxs.append(theory_angle_edges[1:])
                    

    #Convert all the lists of vectors into long single vectors
    value = np.concatenate(value)
    bin1 = np.concatenate(bin1)
    bin2 = np.concatenate(bin2)
    bins = (bin1,bin2)
    angles = np.concatenate(angles)
    if is_binavg:
        angle_mins = np.concatenate(angle_mins)
        angle_maxs = np.concatenate(angle_maxs)
    else:
        angle_mins = None
        angle_maxs = None

    return angles, value, bins, is_binavg, angle_mins, angle_maxs