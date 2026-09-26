from .common import check_magic, child, u, guard, Malformed
from ..state import SESSION

def _summary(valobj, _d):
    check_magic(valobj, "DspBuffer")
    frames, ch = u(valobj, "frames"), u(valobj, "channels")
    rate, cur  = u(valobj, "sample_rate"), u(valobj, "write_cursor")
    data = u(valobj, "samples")
    if rate == 0: raise Malformed("sample_rate is 0")
    dur = frames / rate
    return f"DspBuffer<f32> {ch}ch {frames} frames @{rate}Hz ({dur*1000:.1f}ms) cursor: {cur}/{frames} data: 0x{data:x}"

summary = guard("DspBuffer", _summary)