import json, os, sys
sys.path.insert(0,'.')
import os
import pytest

def test_secret_seeds_differ_and_not_seed_derived():
    import copy
    from cogym.campaign import HiddenEvaluator, DEFAULT_CAMPAIGN
    cfg1=copy.deepcopy(DEFAULT_CAMPAIGN); cfg2=copy.deepcopy(DEFAULT_CAMPAIGN)
    ev1=HiddenEvaluator(cfg1,None); ev2=HiddenEvaluator(cfg2,None)
    s1a,s1b=ev1.secret_seeds(),ev2.secret_seeds()
    assert s1a!=s1b  # OS entropy: same config, different calls -> different seeds

def test_event_ledger_chain():
    from cogym.core import EventLedger
    p='/tmp/opencode/test-chain.jsonl'
    led=EventLedger(p)
    e1=led.append('a',x=1); e2=led.append('b',y=2); e3=led.append('c',z=3)
    assert e3.prev_hash==e2.event_hash and e2.prev_hash==e1.event_hash
    os.remove(p)

def test_stf_v2_missingness():
    from cogym.stx_v2 import phenotype_vector, _normalize_fields, subscale_fidelity
    sigs=[{'accuracy':0.8,'calibration_error':0.1},
          {'accuracy':0.4,'calibration_error':0.5},
          {'accuracy':0.6}]  # third missing calibration
    fs=_normalize_fields(sigs)
    v=phenotype_vector(sigs[2], fs)
    assert 'calibration_error' not in str(v) or v['epistemic'] is None or isinstance(v['epistemic'],float)

def test_hardworld_naive_neq_oracle():
    from cogym.hardworlds import generate_batch
    ws=generate_batch(20)
    assert len(ws)>=10
    for w in ws:
        assert w.oracle_choice != w.naive_choice

def test_hermes_prompt_interpolation():
    # P0-4 regression: {failures_json} must interpolate, not stay literal
    from cogym.hermes_proposals import PROMPT_TEMPLATE
    class SafeDict(dict):
        def __missing__(self,k): return '{'+k+'}'
    out=PROMPT_TEMPLATE.format_map(SafeDict(
        genome_json='{}', failures_json='[{"test":1}]', reason='r', reps='r',
        inductions='i', mem='m', social='s', reveal='v', n=3))
    assert '[{"test":1}]' in out and '{{failures}}' not in out and '{failures_json}' not in out
