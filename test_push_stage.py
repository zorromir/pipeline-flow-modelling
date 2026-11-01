"""Typed, inspectable Rinse -> Dry demonstration; not an industrial cycle solver."""
from dataclasses import dataclass
from .rinse_demo import RinseSettings, RinseResult, simulate_rinse_demo
from .dry_demo import DrySettings, DryResult, simulate_dry_demo


@dataclass(frozen=True)
class RinseDryDemonstration:
    rinse: RinseResult
    dry: DryResult
    @property
    def water_transfer_residual_l(self) -> float:
        return float(self.rinse.transfer.water_in_pipe_l-self.dry.water_remaining_l[0])
    @property
    def product_transfer_residual_l(self) -> float:
        transfer = self.rinse.transfer
        return float(sum(transfer.wall_product_by_segment_l)
                     + sum(transfer.mobile_product_by_segment_l)
                     - self.dry.remaining_product_l)


def run_rinse_to_dry_demo(rinse: RinseSettings | None = None,
                          dry: DrySettings | None = None) -> RinseDryDemonstration:
    r = simulate_rinse_demo(rinse)
    d = simulate_dry_demo(r.transfer, dry)
    return RinseDryDemonstration(r, d)
