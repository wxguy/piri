import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from piri.selection import CandidateResult, choose_result, rank_results
from piri.formats import all_formats


def test_choose_smallest():
    rs = [
        CandidateResult("a", "PASS", archive_bytes=100, compression_seconds=3, integrity=True),
        CandidateResult("b", "PASS", archive_bytes=80, compression_seconds=4, integrity=True),
    ]
    assert choose_result(rs, "smallest").format == "b"


def test_choose_fastest():
    rs = [
        CandidateResult("a", "PASS", archive_bytes=100, compression_seconds=3, integrity=True),
        CandidateResult("b", "PASS", archive_bytes=80, compression_seconds=4, integrity=True),
    ]
    assert choose_result(rs, "fastest").format == "a"


def test_choose_ignores_failed():
    rs = [
        CandidateResult("bad", "FAIL", archive_bytes=1, compression_seconds=0.1, integrity=False),
        CandidateResult("good", "PASS", archive_bytes=100, compression_seconds=3, integrity=True),
    ]
    assert choose_result(rs, "smallest").format == "good"


def test_ar_not_generic_writer():
    ar = next(x for x in all_formats() if x.name == "ar")
    assert ar.write is False


def test_ranking_has_score_and_rank():
    rs = [
        CandidateResult("a", "PASS", archive_bytes=100, compression_seconds=1, integrity=True),
        CandidateResult("b", "PASS", archive_bytes=90, compression_seconds=2, integrity=True),
    ]
    ranked = rank_results(rs, "balanced")
    assert ranked[0].rank == 1
    assert ranked[0].score is not None
