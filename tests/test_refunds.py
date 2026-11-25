from app.modules.refunds.units import original_share


def by_id(data, id):
    return next(x for x in data['refunds'] if x['id']==id)


def test_cross_day_preserves_sale_discount(dirty):
    first=by_id(dirty,'R001')
    assert (first['sale_day'],first['return_day'],first['expected'],first['original_line'])==('2026-11-20','2026-11-21',1633,1)


def test_out_of_order_uses_timestamp(dirty):  # TRAP-13
    first,last=[by_id(dirty,key) for key in ('R001','R002')]
    assert first['source_line']>last['source_line']
    assert (first['returned_qty'],last['returned_qty'],last['expected'])==(1,3,3267)


def test_excess_return_isolated(dirty):
    assert by_id(dirty,'R011')['reason']=='RETURN_OVER_QTY'


def test_missing_line_isolated(dirty):
    assert by_id(dirty,'R012')['reason']=='SALE_LINE_MISSING'


def test_return_before_sale(dirty):
    assert by_id(dirty,'R013')['reason']=='RETURN_BEFORE_SALE'


def test_refunds_for_isolated_sale(dirty):
    assert by_id(dirty,'R010')['reason']=='SALE_ISOLATED'


def test_return_unit_tail_exhausts_discount():
    line={'price':2000,'qty':3,'discount':1100}
    assert [original_share(line,i,1)['expected'] for i in range(3)]==[1633,1633,1634]


def test_ambiguous_missing_sale_distinguished(dirty):
    assert by_id(dirty,'R014')['reason']=='SALE_MISSING'
