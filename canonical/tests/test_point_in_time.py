from datetime import datetime, timedelta, timezone

from cogym.market.features import packet_from_bars
from cogym.market.schema import Bar, PointInTimeDatum


def test_future_data_is_excluded():
    t = datetime(2025, 1, 1, tzinfo=timezone.utc)
    bars = [Bar("X", t + timedelta(minutes=i), 100+i, 101+i, 99+i, 100+i, 1) for i in range(30)]
    now = bars[-1].ts
    ctx = [
        PointInTimeDatum("known", 1, t, now),
        PointInTimeDatum("future", 2, t, now + timedelta(seconds=1)),
    ]
    packet = packet_from_bars(bars, ctx)
    assert [x.key for x in packet.context] == ["known"]
