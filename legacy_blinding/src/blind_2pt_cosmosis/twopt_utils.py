import numpy as np
import os
import logging
from astropy.io import fits
import shutil
from scipy.interpolate import interp1d
from astropy.table import Table

logger = logging.getLogger("2pt_blinding")

# # gambiarra to use the type_table from cosmosis-standard-library
def load_type_table():
    # Taken from:
    # https://github.com/joezuntz/cosmosis-standard-library/
    #     blob/sacc/likelihood/2pt/twopoint_cosmosis.py
    # with Joe Zuntz consent
    dirname = os.path.split(__file__)[0]
    table_name = os.path.join(dirname, "cosmosis_files/type_table.txt")
    type_table = Table.read(table_name, format="ascii.commented_header")
    table = {}
    for (type1, type2, section, x, y) in type_table:
        table[(type1, type2)] = (section, x, y)
    return table

type_table = load_type_table()

class SpectrumInterp(object):
    """
    This is copied from 2pt_like, for get_data_from_dict_for_2pttype

    Should not get used if bin averaging is being used; is in place
    for if theory vector in datablock is very densely sampled, this 
    gets used to pick out values corresponding to desired angle positions
    """
    def __init__(self,angle,spec,bounds_error=True):
        if np.all(spec>0):
            self.interp_func=interp1d(np.log(angle),np.log(spec),bounds_error=bounds_error,fill_value=-np.inf)
            self.interp_type='loglog'
        elif np.all(spec<0):
            self.interp_func=interp1d(np.log(angle),np.log(-spec),bounds_error=bounds_error,fill_value=-np.inf)
            self.interp_type='minus_loglog'
        else:
            self.interp_func=interp1d(np.log(angle),spec,bounds_error=bounds_error,fill_value=0.)
            self.interp_type="log_ang"

    def __call__(self,angle):
        if self.interp_type=='loglog':
            spec=np.exp(self.interp_func(np.log(angle)))
        elif self.interp_type=='minus_loglog':
            spec=-np.exp(self.interp_func(np.log(angle)))
        else:
            assert self.interp_type=="log_ang"
            spec=self.interp_func(np.log(angle))
        return spec

def spectrum_array_from_block(block, section_name, types, xlabel='theta', bin_format = 'bin_{0}_{1}'):
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

def get_dictkey_for_2pttype(type1, type2):
    """
    Convert strings used in fits file to label spectra type in fits file to
    dictionary keys expected by this script's functions.
    (fits file 2pt table naming -> this script's naming)
    """
    logger.debug("Requested: \ttype1: {0:s}, type2: {1:s}".format(type1, type2))
    mapping = {
        'G': 'galaxy',
        'C': 'cmb',
        'P': 'position',
        'E': 'shear_emode',
        'B': 'shear_bmode',
        '+': 'shear_plus',
        '-': 'shear_minus',
        'K': 'kappa',
        'R': 'real',
        'F': 'fourier'
    }

    if type1 in ("GPF", "GEF", "GBF", "GPR", "G+R", "G-R", "CKR", "GPF", "GEF", "GBF"):
        # Translate short codes into longer strings
        newtypes = ['_'.join([mapping[t[0]], mapping[t[1]], mapping[t[2]]]) for t in [type1, type2]]
        type1 = newtypes[0]
        type2 = newtypes[1]

    try:
        section, xlabel, ylabel = type_table[(type1, type2)]
        ykey = section
        xkey = f"{section}_{xlabel}"
    except KeyError:
        raise ValueError("Spectra type not recognized: {0:s}, {1:s} ".format(type1, type2))
    logger.debug("Returning: \txkey: {0:s}, ykey: {1:s}".format(xkey, ykey))
    return xkey, ykey

def get_twoptdict_from_pipeline_data(data):
    """
    Extract 2pt data from a cosmosis pipeline data object and return a dictionary
    with keys corresponding to the 2pt spectra types.

    For auto spectra where z bin label order doesn't matter, both orders
    will be stored. (e.g. the same data will be there for bins 1-2 and 2-1).
    """
    outdict = {}
    type_keys = [types for types in type_table if data.has_section(type_table[types][0])]

    for types in type_keys:
        section, xlabel, binformat = type_table[types]
        xkey, ykey = get_dictkey_for_2pttype(types[0], types[1])
        
        x, y, bins, is_binavg, x_mins, x_maxs = spectrum_array_from_block(data, section, types, xlabel, binformat)
        
        outdict[xkey] = x
        outdict[ykey] = y
        outdict[ykey + '_bins'] = bins
        outdict[ykey + '_binavg'] = is_binavg
        
        if is_binavg:
            outdict[xkey + '_mins'] = x_mins
            outdict[xkey + '_maxs'] = x_maxs
    
    return outdict

def apply_2pt_blinding_and_save_fits(factordict, origfitsfile, outfname=None, outftag="_BLINDED", 
                                     justfname=False,bftype='add', storeseed='notsaved'):
    """
    Given the dictionary of one set of blinding factors,
    the name of a  of a fits file containing unblinded 2pt data,
    and (optional) desired output file name or tag,
    multiplies 2pt data in original fits file by blinding factors and
    saves results (blinded data) into a new fits file.

    If argument is passed for outfname, that will be the name of output file,
    if not, will be <input filename>_<outftag>.fits. The script will check
    that the outfname is different than the original, unblinded file. If they
    match, it will revert to default behavior for naming the blinded file
    so that the unblinded file isn't overwritten.
    > if storeseed=True, will save whatever string is there to entry in fits file

    If justfname == True, doesn't do any file manipulation, just returns
    string of output filename. (for testing)

    bftype can be 'add','mult' or 'mult-nocs'. For data vec d, blinding factor f
        'add' - do additive blinding:
                    d_blind = d_input + f, f = d_shift - d_ref, cov_bl = cov
        'mult' - do multiplicative blinding, scale covmat in blinded file:
                    d_blind = d_input*f, f = d_shift/d_ref, cov_bl = f^T*cov*f
        'multNOCS' - do multiplicative blinding, but without covariance scaling
                    d_blind = d_input*f, f = d_shift/d_ref, cov_bl = cov
    """
    logger.info(f'apply2ptblinding for: {origfitsfile}')
    logger.info(f'bftype: {bftype}')
    # check whether data is already blinded and whether Nbins match
    for table in fits.open(origfitsfile): #look through tables to find 2ptdata
        if table.header.get('2PTDATA'):
            if table.header.get('BLINDED'): #check for blinding
                #if entry not there, or storing False -> not already blinded
                raise ValueError('Data is already blinded!')
                return

    # set up output file
    if outfname == None or outfname==origfitsfile:
        #make sure you can't accidentaly overwrite the original
        #if output filename isn't given, add outftag onto the name of the
        #  unblinded file
        if outftag == None or outftag =='':
            outftag = 'BLINDED-{0:s}-defaulttag'.format(bftype)
        outfname = origfitsfile.replace('.fits','{0}.fits'.format(outftag))


    if not justfname:
        shutil.copyfile(origfitsfile,outfname)

        hdulist = fits.open(outfname, mode='update') #update lets us write over

        #apply blinding factors
        for table in hdulist: #look all tables
            if table.header.get('2PTDATA'):
                factor = get_dictdat_tomatch_fitsdat(table, factordict)

                if bftype=='mult' or bftype=='multNOCS':
                    #print 'multiplying!'
                    table.data['value'] *= factor
                    if bftype=='mult': #store info about how to scale covmat
                        type1 = table.header['QUANT1']
                        type2 = table.header['QUANT2']
                        raise ValueError('Not currently set up to do covariance scaling needed for multiplicative blinding.')

                elif bftype=='add':
                    #print 'adding!'
                    table.data['value'] += factor
                else:
                    raise ValueError('bftype {0:s} not recognized'.format(bftype))

                #add new header entry to note that blinding has occurred, and what type
                table.header['BLINDED'] = bftype
                table.header['KEYWORD'] = storeseed

        hdulist.close() # will save new data to file if 'update' was passed when opened
        logger.info(f">>>> Stored blinded data in {outfname}")
    return outfname

def get_dictdat_tomatch_fitsdat(table, dictdata):
    """
    Given table of type fits.hdu.table.BinTableHDU containing 2pt data,
    retrieves corresponding data from dictionary (blinding factors).

    Expects that same z and theta bin numbers correspond to the same
    z and theta values (i.e. matches up bin numbers but doesn't do
    any interpolation). Theta values will be checked, but z values won't.
    """
    if not table.header.get('2PTDATA'):
        logger.warning("Can't match dict data: this fits table doesn't contain 2pt data. Is named:",table.name)
        return
    type1 = table.header['QUANT1']
    type2 = table.header['QUANT2']

    bin1 = table.data['BIN1'] #which bin is quant1 from?
    bin2 = table.data['BIN2'] #which bin is quant2 from?

    # check for bin averaging
    if "ANGLEMIN" in table.data.names:
        fits_is_binavg = True
        xfromfits_mins =  table.data['ANGLEMIN']
        xfromfits_maxs =  table.data['ANGLEMAX']
    else:
        fits_is_binavg = False
        xfromfits_mins = None
        xfromfits_maxs = None
    
    xfromfits = table.data['ANG']

    yfromdict = get_data_from_dict_for_2pttype(type1, type2, bin1, bin2, xfromfits,
                                               dictdata, fits_is_binavg=fits_is_binavg,
                                               xfits_mins=xfromfits_mins, xfits_maxs=xfromfits_maxs)
    
    return yfromdict

def get_data_from_dict_for_2pttype(type1, type2, bin1fits, bin2fits, xfits, datadict,
                                   fits_is_binavg=True, xfits_mins=None, xfits_maxs=None):
    """
    Given info about 2pt data in a fits file (spectra type, z bin numbers,
    and angular bin numbers, extracts 2pt data from a dictionary of
    e.g. blinding factors to match, with same array format and bin ordering
    as the fits file data.
    """
    xkey,ykey = get_dictkey_for_2pttype(type1,type2)

    is_binavg = datadict[ykey+'_binavg']
    # this check is probably unnecessary, since the data is always bin averaged
    # if dict_is_binavg != fits_is_binavg:
    #     raise ValueError("Theory calc and fits file aren't consistent in whether they do bin averaging vs interpolation for 2pt calculations.")
    if fits_is_binavg and ((xfits_mins is None) or (xfits_maxs is None)):
        raise ValueError("Fits file is bin-averaged but I couldn't find theta values for bin edges.")

    if 'theta' in xkey: #if realspace, put angle data into arcmin
        xmult = 60.*180./np.pi # change to arcmin
    else:
        xmult = 1. #fourier space

    xfromdict = datadict[xkey]*xmult #in arcmin (is in radians in datablock)
    xfromdict = xfromdict*xmult
    if is_binavg:
        xfromdict_mins = datadict[xkey+'_mins']*xmult
        xfromdict_maxs = datadict[xkey+'_maxs']*xmult
    yfromdict = datadict[ykey]
    binsdict = datadict[ykey+'_bins']
    b1dict = binsdict[0]
    b2dict = binsdict[1]

    #if get theory calcs in same format as fits ones
    Nentries = bin1fits.size
    yout = np.zeros(Nentries)
    #this structure will store interp functions for b1-b2 combos
    # so we don't have to keep recreating them
    if not is_binavg:
        Nb1fits = max(bin1fits)
        Nb2fits = max(bin2fits)
        interpfuncs = [[None for b2f in range(Nb2fits)]\
                       for b1f in range(Nb1fits)]

    for i in range(Nentries):
        b1 = bin1fits[i]
        b2 = bin2fits[i]
        if is_binavg:
            wherebinsmatch = (b1==b1dict)*(b2==b2dict)

            roundto=4 #round for matching, since there are more decimals in fits than datablock
            wherexmatch_mins = np.around(xfits_mins[i],roundto)==np.around(xfromdict_mins,roundto)
            wherexmatch_maxs = np.around(xfits_maxs[i],roundto)==np.around(xfromdict_maxs,roundto)
            wherexmatch = wherexmatch_mins*wherexmatch_maxs
            whichinds = wherebinsmatch*wherexmatch
            howmany = np.sum(whichinds)
            if howmany==0: #no matches
                raise ValueError("No theory calc match for data point: {0:s}, z bins = ({1:d},{2:d}), theta between [{3:0.2f},{4:0.2f}]".format(ykey,b1,b2,xfits_mins[i],xfits_maxs[i]))
            elif howmany>1: #duplicate matches
                raise ValueError("More than one theory calc match for data point: {0:s}, z bins = ({1:d},{2:d}), theta between [{3:0.2f},{4:0.2f}]".format(ykey,b1,b2,xfits_mins[i],xfits_maxs[i]))
                
            yout[i] = yfromdict[whichinds]
        else:
            whichinds = (b1==b1dict)*(b2==b2dict)#*(ab==angbdict)
            # get x and y info for that bin combo
            tempx = xfromdict[whichinds]
            tempy = yfromdict[whichinds]
            if interpfuncs[b1-1][b2-1] is None: #no interpfunc yet, set it up
                yinterp = SpectrumInterp(tempx,tempy)
                interpfuncs[b1-1][b2-1] = yinterp
            else:
                yinterp = interpfuncs[b1-1][b2-1]
            yout[i] =  yinterp(xfits[i])
            # We're returning the y data from the dictionary's array
            # interpolated to match the theta values in the fits file.
    return yout