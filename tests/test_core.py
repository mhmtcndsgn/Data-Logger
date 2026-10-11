"""Çekirdek testleri:  python -m pytest tests  (ya da: python tests/test_core.py)"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stm32logger.engine import DemoSerial, Engine  # noqa: E402
from stm32logger.exporter import export_session  # noqa: E402
from stm32logger.importer import load_file  # noqa: E402
from stm32logger.parser import parse_line  # noqa: E402
from stm32logger.session import Session  # noqa: E402


def test_parse_variants():
    assert parse_line("1450").values == [1450.0]
    assert parse_line("1, 2.5,-3,4e2").values == [1.0, 2.5, -3.0, 400.0]
    assert parse_line("1;2;3").values == [1.0, 2.0, 3.0]
    assert parse_line("1\t2").values == [1.0, 2.0]
    assert parse_line("1 2 3").values == [1.0, 2.0, 3.0]
    assert parse_line("1,2,3,").values == [1.0, 2.0, 3.0]          # sondaki virgül
    v = parse_line("5,,1200").values                                # boş alan: kanal kaymaz
    assert v[0] == 5 and v[1] != v[1] and v[2] == 1200
    v = parse_line("5,nan,1200").values
    assert len(v) == 3 and v[2] == 1200
    p = parse_line("Sicaklik:25.3 Nem=60")
    assert p.named == {"Sicaklik": 25.3, "Nem": 60.0}
    assert parse_line("START,5000").kind == "start" and parse_line("START,5000").count == 5000
    assert parse_line("END").kind == "end"
    assert parse_line("BASLA 10").count == 10
    assert parse_line("zaman,adc1,adc2").kind == "header"
    assert parse_line("ADC:1450").named == {"ADC": 1450.0}
    assert parse_line("System ready").kind == "text"                # açılış mesajı kanal adı olmaz
    assert parse_line("Boot 3").kind == "text"
    assert parse_line("# yorum").kind == "text"


def _feed(s, lines):
    for i, ln in enumerate(lines):
        s.add(float(i), parse_line(ln))
    s.finish("test")


def test_seq_gap_detection():
    s = Session(mode="dma")
    lines = ["START,2000"] + [f"{i},{i*2}" for i in range(2000) if not (1450 < i < 1780)] + ["END,2000"]
    _feed(s, lines)
    assert s.has_seq is True
    assert s.n == 2000 - 329
    assert len(s.gaps) == 1 and s.gaps[0].after_seq == 1450 and s.gaps[0].next_seq == 1780
    assert s.missing == 329
    assert s.channels == ["Kanal 1"]


def test_header_and_named():
    s = Session()
    _feed(s, ["sira,ivme,sicaklik", "0,1.5,20", "1,1.6,21", "2,1.7,22", "3,1.8,23"])
    assert s.has_seq and s.channels == ["ivme", "sicaklik"] and s.n == 4
    s2 = Session()
    _feed(s2, ["T:20 H:40", "T:21 H:41", "T:22"])
    assert s2.channels == ["T", "H"] and s2.n == 3
    assert s2.cols[1][2] != s2.cols[1][2]  # NaN


def test_engine_dma_demo_no_loss():
    with tempfile.TemporaryDirectory() as d:
        ser = DemoSerial(mode="dma", baud=2_000_000, n_samples=20000)
        ser._pending_dump = time.perf_counter()
        eng = Engine(ser, mode="dma", raw_path=os.path.join(d, "raw.txt"), idle_timeout=0.5,
                     session_factory=lambda: Session(mode="dma", sample_rate=1000))
        eng.start()
        done = None
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                done = eng.done_q.get(timeout=0.1)
                break
            except Exception:
                pass
        eng.stop()
        assert done is not None, "aktarım bitmedi"
        assert done.finish_reason == "end"
        assert done.n == 20000 and done.missing == 0 and done.expected == 20000
        assert done.channels == ["Kanal 1", "Kanal 2"]
        assert os.path.getsize(os.path.join(d, "raw.txt")) > 100000

        for fmt in ("txt", "csv", "xlsx"):
            p = export_session(done, os.path.join(d, f"out.{fmt}"), fmt, "tr")
            back = load_file(p)
            assert back.n == 20000, fmt
            assert back.channels == ["Kanal 1", "Kanal 2"], (fmt, back.channels)
            assert back.has_seq and back.missing == 0
            assert abs(back.sample_rate - 1000) < 1e-6, (fmt, back.sample_rate)


class _BurstSerial:
    """Hiç beklemeden, rastgele parçalara bölünmüş dev bir aktarım verir."""

    def __init__(self, payload: bytes):
        import random
        self._data = payload
        self._pos = 0
        self._rnd = random.Random(1)
        self.timeout = 0.05

    @property
    def in_waiting(self):
        return len(self._data) - self._pos

    def read(self, n=1):
        if self._pos >= len(self._data):
            time.sleep(self.timeout)
            return b""
        k = min(n, self._rnd.randint(1, 4096))
        out = self._data[self._pos:self._pos + k]
        self._pos += k
        return out

    def write(self, b):
        return len(b)

    def close(self):
        pass


def test_engine_burst_300k_lines_no_loss():
    n = 300_000
    payload = ("START,%d\r\n" % n + "".join(f"{i},{i % 4096},{(i * 7) % 4096}\r\n" for i in range(n))
               + "END,%d\r\n" % n).encode()
    eng = Engine(_BurstSerial(payload), mode="dma", idle_timeout=0.5,
                 session_factory=lambda: Session(mode="dma"))
    t0 = time.perf_counter()
    eng.start()
    done = eng.done_q.get(timeout=60)
    dt = time.perf_counter() - t0
    eng.stop()
    assert done.n == n and done.missing == 0 and not done.gaps
    assert done.cols[0][12345] == 12345 % 4096
    print(f"    {n} satır {dt:.2f} sn'de işlendi ({n / dt:,.0f} satır/sn, {len(payload) / dt / 1e6:.1f} MB/sn)")


def test_robust_against_corruption():
    # aşırı büyük sayı motoru çökertmemeli
    s = Session(mode="dma")
    _feed(s, ["START,6"] + [f"{i},{i}" for i in range(3)] + ["1e400,5", "99999999999999999999,1"]
          + [f"{i},{i}" for i in range(3, 6)] + ["END,6"])
    assert s.n == 6 and s.bad_lines == 2 and s.missing == 0

    # tek bozuk sıra no ("1234" yerine "34"): sahte 1200 kayıp üretmemeli
    s = Session(mode="live")
    lines = [f"{i},{i * 2}" for i in range(1220, 1234)] + ["34,2468"] + [f"{i},{i * 2}" for i in range(1235, 1250)]
    _feed(s, lines)
    assert s.missing == 0 and s.fixed_seq == 1 and s.seq[14] == 1234

    # birleşmiş iki satır (kayıp \r\n): satır reddedilir, kayıp doğru sayılır, hayalet kanal yok
    s = Session(mode="live")
    lines = [f"{i},{i},{i}" for i in range(20)] + ["20,20,2021,21,21"] + [f"{i},{i},{i}" for i in range(22, 30)]
    _feed(s, lines)
    assert len(s.channels) == 2 and s.bad_lines == 1 and s.missing == 2

    # 16 bit sayaç taşması kayıp sayılmaz
    s = Session(mode="live")
    _feed(s, [f"{i % 65536},1" for i in range(65530, 65545)])
    assert s.missing == 0 and s.out_of_order == 0 and s.n == 15


def test_connect_mid_stream():
    # bağlantı satırın ortasında açıldı: ilk satır yarım ("30,2730" yerine "1230,2730,9")
    s = Session(mode="live")
    lines = ["30,2730"] + [f"{i},{i % 97},{i % 13}" for i in range(1231, 1300) if i != 1260]
    _feed(s, lines)
    assert s.has_seq and s.channels == ["Kanal 1", "Kanal 2"]
    assert s.bad_lines == 1 and s.missing == 1 and s.gaps[0].after_seq == 1259


def test_boot_text_before_data():
    s = Session(mode="dma")
    _feed(s, ["System ready", "Boot 3", "START,4", "0,1,2", "1,1,2", "2,1,2", "3,1,2", "END,4"])
    assert s.channels == ["Kanal 1", "Kanal 2"] and s.n == 4 and s.missing == 0


def test_old_format_import():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "eski.txt")
        with open(p, "w", encoding="utf-8") as f:
            for i in range(10):
                f.write(f"[2025-06-25 16:35:{i:02d}] Sicaklik:{20+i}.5\n")
        s = load_file(p)
        assert s.n == 10 and s.channels == ["Sicaklik"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            t = time.perf_counter()
            fn()
            print(f"OK  {name}  ({time.perf_counter()-t:.2f}s)")
