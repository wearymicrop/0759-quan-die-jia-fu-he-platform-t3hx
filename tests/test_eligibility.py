def findings(data, sale):
    return {row['coupon']:row for row in data['eligibility'][sale]['findings']}


def test_qualified_by_eligible_category(clean):
    assert findings(clean,'000731')['品类九折']['eligible_gross']==6000


def test_minimum_on_order(clean):
    assert findings(clean,'000733')['店券5']['reason']=='MINIMUM_NOT_MET'


def test_wrong_shop(clean):
    assert findings(clean,'000731')['联店券']['reason']=='SHOP_MISMATCH'


def test_wrong_category(clean):
    assert findings(clean,'000740')['品类九折']['reason']=='CATEGORY_MISMATCH'


def test_explicitly_permitted_and_default_deny(clean):
    matrix=clean['eligibility']['000731']['matrix']
    assert {'a':'品类九折','b':'店券5','reason':'COMPATIBLE'} in matrix
    assert {'a':'品类九折','b':'直减8','reason':'PAIR_UNDECLARED'} in matrix


def test_same_group_overrides_edge(clean):  # TRAP-19
    assert {'a':'店券3','b':'店券5','reason':'EXCLUSIVE_GROUP'} in clean['eligibility']['000731']['matrix']


def test_ambiguous_version_blocks_order(dirty):
    row=dirty['eligibility']['000750']
    assert row['blocked'] and row['qualified']==[]
    assert row['findings'][0]['rule_indices']==[11,12]
