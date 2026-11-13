# [MODIFIED: SingleValue_Example.py] Original repo script, inputs set for the
# 6 ft Rocketman at 23 lb, D0 formula fixed, and one more fix:
#   evaluate_mit returns an array, so mit_sol is indexed with [0] before printing,
#   and plt.show() is moved to the end so results print before plots open.
#   Look for the [MODIFIED] comment near the bottom.

import numpy as np
import pickle
from interpolating_functions import evaluate_pflanz, evaluate_mit # Import the function
from interpolating_functions import plot_pflanz_interpolation, plot_MIT_interpolation # Import the function
import matplotlib.pyplot as plt

#### EXTRACTING INTERPLATOR DATA FROM PICKLE FILE
# Load the interpolators
with open("combined_data.pkl", "rb") as f:
    data = pickle.load(f)

################################################################################
######################## Define recovery parameters ############################
################################################################################

atm_density = 1.172 # Air density at 1500 ft (standard atmosphere)  [kg/m^3]
mass        = 10.43 # 23 lb descent mass                          [kg]
v_ls        = 30.48 # 100 ft/s at line stretch                    [m/s]

g           = 9.81  # Gravitational Acceleration                        [m/s^2]  

CD0         = 1.236 # Rocketman Cd 2.2 converted to canopy area    [-]
S0          = 4.530 # 6 ft Rocketman canopy area, 48.76 ft^2 (5 ft: 3.146) [m^2]
D0          = np.sqrt(4*S0/np.pi) # [MODIFIED] repo line was 4*np.sqrt(12/np.pi) [m]

Cx          = 1.6   # Opening force coefficient (assumed)        [-]

nfill       = 9     # Canopy fill constant (assumed)             [-]

################################################################################
############################### Computation ####################################
################################################################################

tf          = nfill*D0/v_ls     # Parachute inflation time              [s]

A_ballistic = 2*mass/(S0*CD0*atm_density*v_ls*tf) # Ballistic Parameter [-]

Rm          = atm_density*(S0*CD0)**(3/2)/mass     # Mass Ratio         [-]

# Following OSCalc Manual: Choose which value you prefer:
if Rm > 0.1:
    Drag_integral = 0.5 # Between 0.4 and 0.5
elif Rm > 0.01:
    Drag_integral = (0.5+0.2)/2
else:
    Drag_integral = 0.2

n_gen_fill = v_ls*tf*Drag_integral/np.sqrt(S0*CD0)

force_nominal = 0.5*atm_density*(v_ls**2)*S0*CD0
print(f'Steady State Force = {force_nominal:.2f} N')

# Values according to Pflanz
pflanz_sol = evaluate_pflanz(data,'0.5', A_ballistic)
fig1, ax1 = plt.subplots() 
plot_pflanz_interpolation(data, '0.5', A_ballistic, pflanz_sol, ax1)
print(f'Pflanz X1 = {pflanz_sol:.4f}')
print(f'Pflanz Ck = {pflanz_sol*Cx:.4f}')
print(f'Pflanz Force = {pflanz_sol*Cx*force_nominal:.2f} N')

# Values according to MIT
mit_sol = evaluate_mit(data, n_gen_fill, Rm)
fig2, ax2 = plt.subplots()
plot_MIT_interpolation(data, n_gen_fill, Rm, mit_sol, ax2)
mit_sol = mit_sol[0]  # [MODIFIED] evaluate_mit always returns an array; take the single value
print(f'MIT Ck = {mit_sol:.4f}')
print(f'MIT Force = {mit_sol*force_nominal:.2f} N')
plt.show()  # show plots last so the prints appear before the windows block








