import sqlite3
from concurrent.futures import ThreadPoolExecutor

from app.config import db_path


def test_trace_links_source_lines(dirty):
    packet=dirty['trace']['packets'][0]
    assert packet['receipt_line']==1
    assert [r['rule_index'] for r in packet['applied']]==[2,3]
    assert {r['id'] for r in packet['returns']}=={'R001','R002','R011','R012','R013'}


def test_orphan_exportable(dirty):
    assert [r['id'] for r in dirty['trace']['orphan_returns']]==['R014']


def test_full_evidence_download(client):
    run=client.post('/api/runs',json={'sample':'dirty'}).json()
    response=client.get(f"/api/runs/{run['id']}/export")
    assert response.headers['content-disposition'].startswith('attachment;')
    assert response.json()['result']['trace']['packets'][0]['returns'][1]['expected']==1633


def test_replay_with_persisted_model(client):
    r=client.post('/api/runs',json={'sample':'dirty'}).json()
    assert client.post(f"/api/runs/{r['id']}/rerun").json()=={**r,'reused':True}
    assert client.get(f"/api/runs/{r['id']}").json()['manifest']==r['manifest']


def test_parallel_replays_insert_once(client):
    def create(_):
        return client.post('/api/runs',json={'sample':'clean'}).json()
    with ThreadPoolExecutor(4) as pool:
        results=list(pool.map(create,range(4)))
    assert len({r['id'] for r in results})==1
    assert [r['reused'] for r in results].count(False)==1
    with sqlite3.connect(db_path()) as conn:
        assert conn.execute('SELECT COUNT(*) FROM runs').fetchone()[0]==1


def test_unknown_trace(client):
    r=client.get('/api/runs/missing')
    assert r.status_code==404 and r.json()['code']=='RUN_NOT_FOUND'


def test_invalid_rulebook_atomic(client):
    r=client.post('/api/runs',json={'events':'\n','rules':{}})
    assert r.status_code==422 and r.json()['code']=='BAD_RULEBOOK'
    with sqlite3.connect(db_path()) as conn:
        assert conn.execute('SELECT COUNT(*) FROM runs').fetchone()[0]==0
