from cogym.market.challenge import ChallengeSpec, CommitRevealRound, participant_commit


def test_commit_reveal_seed_is_deterministic_and_bound():
    c = ChallengeSpec("c1", "world-v1", "rules-v1", {"level": 3})
    commits = (
        participant_commit("a", "aaa", "n1"),
        participant_commit("b", "bbb", "n2"),
    )
    r = CommitRevealRound.create(c, commits, "server")
    assert r.derive_seed("server") == r.derive_seed("server")
    try:
        r.derive_seed("wrong")
        assert False
    except ValueError:
        pass
