
import os
import sys
import argparse
import logging

from tqdm import tqdm
from pyopenms import MSExperiment
from pyopenms import MzMLFile

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(filename)s %(funcName)s - %(levelname)s: %(message)s'
)
LOGGER = logging.getLogger()


def adjust_file(experiment, ppm=None, th=None):
    '''
    Shift all m/z values in experiment by either the specified ppm or Thomsons.
    Either ppm or th must be specified. The ppm and th options are mutually exclusive.

    Parameters
    ----------
    experiment: pyopenms.MSExperiment
        Initialized MSExperiment object.
    ppm: float
        Mass shift in ppm
    th: float
        Mass shift in Thomson

    '''
    if int(ppm is None) + int(th is None) != 1:
        LOGGER.error('ppm or th must be specified.')
    
    if ppm is not None:
        adjust_mass_f = lambda mz: mz + (mz * (ppm / 1e6))
    if th is not None:
        adjust_mass_f = lambda mz: mz + th

    spectra = experiment.getSpectra()
    for scan_i in tqdm(range(len(spectra))):
        mzs, ints = spectra[scan_i].get_peaks()
        for mz_i in range(len(mzs)):
            mzs[mz_i] = adjust_mass_f(mzs[mz_i])
        spectra[scan_i].set_peaks((mzs, ints))

    experiment.setSpectra(spectra)
    experiment.updateRanges()


def main():
    parser = argparse.ArgumentParser(description='Adjust all m/z in a mzML file by a specified mass or ppm.')

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('--inPlace', action='store_true', default=False, dest='in_place',
                              help='Should mzML be modified in place?')
    output_group.add_argument('--suffix', default='', help='Add suffix after output file basename.')
    output_group.add_argument('-o', '--ofname', help='Specify output file name.')

    adjust_group = parser.add_mutually_exclusive_group(required=True)
    adjust_group.add_argument('-p', '--ppm', type=float, default=None,
                              help='Mass adjustment in parts per million (ppm)')
    adjust_group.add_argument('-t', '--th', type=float, default=None,
                              help='Mass adjustment in Thomson (Th)')

    parser.add_argument('mzML', help='The mzML file to adjust.')

    args = parser.parse_args()

    # determine output file name
    ofname = None
    if args.in_place:
        ofname = args.mzML
    elif args.suffix:
        base, ext = os.path.splitext(args.mzML)
        ofname = f'{base}_{args.suffix}{ext}'
    elif args.ofname:
        ofname = args.ofname
    else:
        LOGGER.error('Not able to determine output file name from arguments!')
        sys.exit(1)

    # load msML file
    LOGGER.info(f'Loading "{args.mzML}"')
    experiment = MSExperiment()
    MzMLFile().load(args.mzML, experiment)
    LOGGER.info(f'Done loading "{args.mzML}"')

    # adjust m/z values
    LOGGER.info('Adjusting m/z values')
    adjust_file(experiment, args.ppm, args.th)

    # write file
    LOGGER.info(f'Writing adjusted values to: "{ofname}"')
    MzMLFile().store(ofname, experiment)


if __name__ == '__main__':
    main()

