from app.modules.reconcile.balance import balance


def test_clean_totals(clean):
    result=clean['reconcile']
    assert result['status']=='MATCHED'
    assert result['totals']==dict(gross=138306,discount=1801,due=136505,paid=136505,refunded=6800,cash_refunded=6800,retained=129705)


def test_difference_by_receipt_not_just_batch(dirty):
    result=dirty['reconcile']
    assert result['status']=='DIFFERENCE'
    assert [(r['id'],r['gap']) for r in result['differences']]==[('000732',1),('R004',-1)]


def test_dirty_receipt_and_return_coverage(dirty):
    result=dirty['reconcile']
    assert (result['row_gap'],result['sales_isolated'],result['returns_isolated'])==(0,1,5)


def test_all_returned_balance(dirty):
    line=next(x for x in dirty['reconcile']['lines'] if x['order']=='000731')
    assert (line['actual'],line['refunded'],line['retained'],line['retained_qty'])==(4900,4900,0,0)


def test_partial_tail_and_zero_cash(dirty):
    line=next(x for x in dirty['reconcile']['lines'] if (x['order'],x['line'])==('000732','01'))
    assert (line['retained_gross'],line['retained_discount'],line['refunded_qty'],line['refunded'])==(2,0,1,0)


def test_missing_row_detected(clean):
    d=balance(clean['receipts'],clean['optimizer'],clean['refunds'][1:])
    assert d['row_gap']==1 and d['status']=='DIFFERENCE'


def test_structural_gaps_are_zero_even_when_cash_differs(dirty):
    result=dirty['reconcile']
    assert (result['formula_gap'],result['retention_gap'])==(0,0)
    assert result['totals']['due']-result['totals']['refunded']==129705
