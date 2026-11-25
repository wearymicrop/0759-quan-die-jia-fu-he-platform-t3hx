from app.modules.optimizer.allocation import allocate, simulate
from app.modules.optimizer.solver import solve


def test_beats_highest_single_coupon(clean):
    row=clean['optimizer'][0]
    assert (row['chosen'],row['due'],row['trial_count'])==(['品类九折','店券5'],4900,7)
    assert {'codes':['直减8'],'due':5200} in row['trials']


def test_rounding_tail_stable_id(clean):  # TRAP-24
    row=clean['optimizer'][1]
    assert row['applied'][0]['shares']=={'01':1,'02':0}
    assert row['due']==5


def test_discount_priority_previous_balance(clean):
    sale=clean['optimizer'][0]
    assert [item['base'] for item in sale['applied']]==[6000,5400]
    assert [item['amount'] for item in sale['applied']]==[600,500]


def test_changing_rule_order_does_not_change_solution(clean):
    q=clean['eligibility']['000731']
    reversed_q={**q,'qualified':list(reversed(q['qualified']))}
    assert solve(clean['receipts']['sales'][0],reversed_q)['chosen']==['品类九折','店券5']


def test_largest_remainder_uses_balance_not_serial_rounding():
    assert allocate(5,{'甲':10,'乙':20,'丙':30})=={'甲':1,'乙':2,'丙':2}


def test_caps_fixed_value_at_item_balance():
    rule=dict(code='券',version='一',source_index=1,kind='fixed',value=20,eligible=['A'])
    net, applied=simulate({'A':3,'B':6},[rule])
    assert net=={'A':0,'B':6} and applied[0]['amount']==3


def test_blocked_version_does_not_guess(dirty):
    bad=next(r for r in dirty['optimizer'] if r['id']=='000750')
    assert bad['status']=='isolated' and 'due' not in bad


def test_zero_face_coupon_is_dropped(clean):
    q=clean['eligibility']['000731']
    new={**q,'qualified':[{**q['qualified'][0],'value':0}],'matrix':[]}
    row=solve(clean['receipts']['sales'][0],new)
    assert row['due']==6000 and row['chosen']==[]
