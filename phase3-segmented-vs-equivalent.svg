"""Reproduce the public Phase 5 uncertainty-band figure; no datasets needed.

Model: published rigid liquid-column balance, hypothetical independent uniforms.
This is a simplified demo, not industrial calibration or validated prediction.
"""
from pathlib import Path
from math import pi

import numpy as np
from scipy.stats import qmc
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N, SEED = 256, 20261101
D, L0, RHO, POUT = 0.20, 100.0, 1000.0, 101325.0
GAS0, N_POLYTROPIC, GOAL = 2., 1.2, .50
AREA = pi*D**2/4
BOUNDS = np.array([[370000, 620000], [.015, .035], [2., 6.], [.10, .30]])


def simulate(parameters):
    p0, friction, K, beta = parameters
    def rhs(t, state):
        velocity, x = state
        L = max(L0-x, 1e-7)
        pressure = p0*(GAS0/(GAS0+AREA*x))**N_POLYTROPIC
        driving = (pressure-POUT)/RHO
        accel = (beta*(1-beta)*velocity**2+driving
            -friction/(2*D)*(1-beta+beta**2/3)*L*velocity*abs(velocity)
            -K/2*(1-beta)**2*velocity*abs(velocity)) / ((1-beta/2)*L)
        return [accel, velocity]
    target = GOAL*L0/(1-beta)
    def stop(t, state): return state[1]-target
    stop.terminal, stop.direction = True, 1
    sol = solve_ivp(rhs, (0,120), (0,0), events=stop, method="DOP853",
                    rtol=2e-7, atol=2e-9, max_step=.18, dense_output=True)
    if not sol.success or not len(sol.t_events[0]):
        raise RuntimeError("Not all samples reached the goal; no selective filtering")
    final_time = float(sol.t_events[0][0])
    time = np.linspace(0, final_time, 75)
    v, x = sol.sol(time)
    # Progress is discharge / discharge target; interpolation is valid as x increases.
    progress = x/target
    return final_time, np.interp(np.linspace(0,1,51), progress, AREA*(1-beta)*v*1000)


def main():
    u = qmc.Sobol(d=4, scramble=True, seed=SEED).random_base2(m=8)
    parameters = BOUNDS[:,0]+u*(BOUNDS[:,1]-BOUNDS[:,0])
    runs = [simulate(row) for row in parameters]
    times = np.array([r[0] for r in runs])
    curves = np.stack([r[1] for r in runs])
    q10, q50, q90 = np.quantile(curves,[.1,.5,.9],axis=0)
    x = np.linspace(0,100,51)
    fig, ax = plt.subplots(figsize=(9.7,4.7),layout="constrained")
    ax.fill_between(x,q10,q90,color="#24766e",alpha=.18,label="10th–90th sample percentiles")
    ax.plot(x,q50,color="#24766e",lw=2.7,label="Sample median")
    ax.set(xlabel="Progress towards the discharge target (%)",
           ylabel="Outlet product flow (L/s)",xlim=(0,100),ylim=(0,max(q90)*1.1))
    ax.set_title("Modelled discharge under uncertain inputs",loc="left",fontsize=19)
    ax.grid(alpha=.2)
    ax.legend(frameon=False)
    target_file=Path(__file__).resolve().parent / "phase5-qmc-flow-reproduced.svg"
    fig.savefig(target_file,bbox_inches="tight")
    print("Samples:",N,"seed:",SEED)
    print("Completion time sample p10/median/p90:",np.quantile(times,[.1,.5,.9]))
    print("Saved",target_file)

if __name__ == "__main__":
    main()
