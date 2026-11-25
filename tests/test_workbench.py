from app.sources import load_sample


def test_every_module_returns_computation(client,dirty):
    assert client.get('/api/health').json()['status']=='ok'
    for section,result in dirty.items():
        assert client.get(f'/api/samples/dirty/{section}').json()==result


def test_clean_preview_and_unknown_sample(client):
    assert client.get('/api/samples/clean').json()['reconcile']['totals']['due']==136505
    assert client.get('/api/samples/no').status_code==404


def test_own_flow_same_engine(client):
    result=client.post('/api/runs',json=load_sample('clean')).json()
    assert result['sample']=='自备数据'
    assert result['result']['reconcile']['status']=='MATCHED'


def test_html_has_navigation(client):
    response=client.get('/')
    assert response.status_code==200
    assert response.text.count('data-panel=')==7
    assert client.get('/static/coupon-grid.js').status_code==200
