import pytest

from app.modules.receipts.intake import read
from app.modules.receipts.money import cents


def test_clean_counts(clean):
    assert clean['receipts']['counts']==dict(input=18,accepted=18,empty=0,duplicates=0,isolated=0)


def test_bom_and_leading_zero(dirty):  # TRAP-02 TRAP-08
    first=dirty['receipts']['sales'][0]
    assert (first['id'],first['source_line'],first['lines'][0]['id'])==('000731',1,'01')


def test_cents_normalized(clean):  # TRAP-06
    row=next(s for s in clean['receipts']['sales'] if s['id']=='000741')
    assert row['lines'][0]['price']==123450


def test_ambiguous_sentinel_isolated(dirty):  # TRAP-07
    row=dirty['receipts']['rows'][-1]
    assert row['code']=='BAD_EVENT' and '未知' in row['raw']


def test_duplicate_normalized_clock(dirty):  # TRAP-11
    replay=next(r for r in dirty['receipts']['rows'] if r['code']=='DUPLICATE_REPLAY')
    assert (replay['id'],replay['line'])==('000731',29)


def test_conflicting_sale_not_last_write(dirty):  # TRAP-14
    assert [r['code'] for r in dirty['receipts']['rows'] if r.get('id')=='000751']==['DUPLICATE_CONFLICT']*2
    assert all(s['id']!='000751' for s in dirty['receipts']['sales'])


def test_truncation_not_counted(dirty):  # TRAP-16
    assert dirty['receipts']['rows'][27]['code']=='BAD_JSON'


def test_no_float_or_overprecision():  # TRAP-10
    assert cents('0.29')==29
    with pytest.raises(ValueError):
        cents('0.295')


def test_empty_and_malformed_are_distinct():  # TRAP-18
    assert read('')['counts']['input']==0
    assert read('\n')['rows'][0]['code']=='EMPTY_ROW'
    assert read('[]')['rows'][0]['code']=='BAD_JSON'
