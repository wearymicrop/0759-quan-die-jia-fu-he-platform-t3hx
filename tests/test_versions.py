import pytest

from app.errors import DomainError
from app.modules.versions.effective import active_version, classify
from app.modules.versions.registry import load
from app.sources import load_sample


def test_overlap_evidence_points_to_both_versions(dirty):  # TRAP-25
    clash=dirty['versions']['conflicts'][0]
    assert clash['code']=='并发券' and clash['source_indices']==[11,12]


def test_boundary_half_open(clean):  # TRAP-23
    cut='2026-11-20T16:00:00.000000+00:00'
    assert active_version(clean['versions'],'换档券',cut)[0]['version']=='新版'
    assert clean['versions']['conflicts']==[]


def test_inactive_version_keeps_sources(clean):
    rule, reason, found=active_version(clean['versions'],'商城旧券','2026-11-20T16:00:00.000000+00:00')
    assert (rule,reason,found[0]['source_index'])==(None,'RULE_INACTIVE',10)


def test_unknown_rule(clean):
    assert active_version(clean['versions'],'并发券','2026-11-20T16:00:00.000000+00:00')==(None,'RULE_UNKNOWN',[])


def test_pairs_normalize_symmetry():
    raw=load_sample('clean')['rules']
    raw['pairs'].append(list(reversed(raw['pairs'][0])))
    assert len(load(raw)['pairs'])==3


def test_broken_edge_rejected():
    raw=load_sample('clean')['rules']
    raw['pairs'].append(['虚构','店券5'])
    with pytest.raises(DomainError,match='兼容边无效'):
        load(raw)


def test_reordered_versions_still_ambiguous():
    book=load_sample('dirty')['rules']
    book['versions'].reverse()
    assert active_version(classify(load(book)),'并发券','2026-11-20T16:00:00.000000+00:00')[1]=='VERSION_OVERLAP'
