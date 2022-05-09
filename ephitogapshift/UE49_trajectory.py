'''
Created on 7 Apr 2022

@author: oqb
'''

# Import the library
import argparse
import ephitogapshift


if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-e','--Emin', type=float, required=True)
    parser.add_argument('-E','--Emax', type=float, required=True)
    parser.add_argument('-p','--Phimin', type=float, required=True)
    parser.add_argument('-P','--Phimax', type=float, required=True)
    parser.add_argument('-s','--steps', type=int, required=True)
    parser.add_argument('-o','--output', type=str, required=False)
    # Parse the argument
    args = parser.parse_args()# Print "Hello" + the user input argument
    
    print('loading data from ../bin/UE49_gapshift.idt')
    gapshift_2_Ephi = ephitogapshift.GapShiftEnergyPhase('../bin/UE49_gapshift.idt')
    print('creating reverse lookup table. This could take some time.')
    gapshift_2_Ephi.create_inverse_lookups()
    
    if args.Phimin == args.Phimax:
        print('fixed angle')
        egraster = ephitogapshift.UndulatorMotion([args.Emin,args.Emax],args.Phimin,gapshift_2_Ephi,args.steps)
        
        
    elif args.Emin == args.Emax:
        print('fixed energy')
        egraster = ephitogapshift.UndulatorMotion(args.Emin,[args.Phimin,args.Phimax],gapshift_2_Ephi,args.steps)
        
        
    else:
        egraster = ephitogapshift.UndulatorMotion([args.Emin,args.Emax],[args.Phimin,args.Phimax],gapshift_2_Ephi,args.steps)
        
    egraster.create_motion_trajectory()
    egraster.check_valid_motion()
    
    print('saving output')
    egraster.save_motion_txt()
    