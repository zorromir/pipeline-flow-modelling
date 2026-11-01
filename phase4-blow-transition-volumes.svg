"""Three original source-code figures for Phase 6; all inputs hypothetical."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow.rinse_demo import simulate_rinse_demo
from pipeline_flow.dry_demo import DrySettings, simulate_dry_demo
from pipeline_flow.stage_handoff import run_rinse_to_dry_demo

OUT = Path(__file__).resolve().parents[1] / 'figures'
OUT.mkdir(exist_ok=True)
INK='#20343a'; DIM='#53666a'; TEAL='#24766e'; BLUE='#467f9b'; WARM='#b98666'


def axes(title: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10.8, 4.9), layout='constrained')
    fig.patch.set_facecolor('#f8faf8')
    ax.set_facecolor('white')
    ax.set_title(title, loc='left', color=INK, fontsize=18, pad=19)
    ax.set_xlabel('Time since start of Rinse (s)', color=DIM)
    ax.set_ylabel(ylabel, color=DIM)
    ax.grid(color='#dbe4e0', linewidth=.8)
    ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    return fig, ax


def save(fig, stem):
    for format in ('png','svg'):
        fig.savefig(OUT / (stem+'.'+format), dpi=180, bbox_inches='tight')
    plt.close(fig)


def main():
    coupled = run_rinse_to_dry_demo()
    rinse = coupled.rinse; dry = coupled.dry
    t_handoff = rinse.transfer.time_s
    w_r = rinse.water_by_segment_l.sum(axis=1)
    w_d = dry.water_remaining_l

    fig,ax = axes('Rinse to Dry: remaining water in the pipe','Illustrative water inventory (L)')
    ax.plot(rinse.time_s, w_r, color=BLUE, lw=2.8, label='Rinse: water accumulation and outflow')
    ax.plot(dry.total_time_s, w_d, color=TEAL, lw=2.8, label='Dry: assumed first-order removal')
    ax.axvline(t_handoff,color=WARM,lw=1.5,linestyle='--')
    ax.annotate('Rinse / Dry transfer',xy=(t_handoff, w_d[0]),
                xytext=(t_handoff+4,max(w_r)*.86),fontsize=10,color=DIM,
                arrowprops={'arrowstyle':'-', 'color':WARM})
    ax.legend(frameon=False, fontsize=10, loc='upper right')
    ax.set(xlim=(0,dry.total_time_s[-1]+3),ylim=(0,max(w_r)*1.16))
    save(fig,'phase6-rinse-dry-water-inventory')

    fig,ax = axes('Rinse: product conservation during illustrative removal','Product inventory / exported product (L)')
    ax.plot(rinse.time_s,rinse.wall_product_by_segment_l.sum(axis=1),
            color=BLUE,lw=2.6,label='Remaining wall product')
    ax.plot(rinse.time_s,rinse.mobile_product_by_segment_l.sum(axis=1),
            color=WARM,lw=2.6,label='Mobile product in pipe')
    ax.plot(rinse.time_s,rinse.discharged_product_l,
            color=TEAL,lw=2.6,label='Cumulative discharged product')
    ax.legend(frameon=False,fontsize=10)
    save(fig,'phase6-rinse-product-balance')

    fig,ax = axes('Dry: sensitivity to assumed water-removal coefficient',
                  'Remaining water / water at Dry start')
    for k,color in ((.010,BLUE),(.026,TEAL),(.045,WARM)):
        y=simulate_dry_demo(rinse.transfer,
            DrySettings(water_removal_rate_per_s=k,target_removed_fraction=.9,max_duration_s=125))
        ax.plot(y.local_time_s,y.water_remaining_l/rinse.transfer.water_in_pipe_l,
                color=color,lw=2.6,label=f'Assumed k = {k:.3f} s⁻¹')
    ax.set_xlabel('Elapsed time within Dry (s)',color=DIM)
    ax.axhline(.10,color='#94a5a3',lw=1.1,ls='--',label='Illustrative 90% removed target')
    ax.set(xlim=(0,125),ylim=(0,1.03))
    ax.legend(frameon=False,fontsize=10)
    save(fig,'phase6-dry-rate-sensitivity')

    print('Rinse stop time (s):',round(t_handoff,3))
    print('Rinse input water (L):',round(float(rinse.injected_water_l[-1]),5))
    print('Water inventory at Rinse/Dry handoff (L):',round(float(w_d[0]),5))
    print('Dry stop reason:',dry.stop_reason)
    print('Dry end time relative to Dry start (s):',round(float(dry.local_time_s[-1]),5))
    print('Water left at Dry stop (L):',round(float(w_d[-1]),5))
    print('Max Rinse water balance residual:',np.max(np.abs(rinse.water_balance_residual_l)))
    print('Max Rinse product balance residual:',np.max(np.abs(rinse.product_balance_residual_l)))
    print('Rinse-Dry transfer residual:',coupled.water_transfer_residual_l)

if __name__=='__main__':
    main()
