from pathlib import Path

import pytest

from iglink.graph_creator import GraphCreator


@pytest.fixture
def graph_creator():
    return GraphCreator()

def test(graph_creator):
    base_dir = Path(__file__).resolve().parents[1]

    exclude_friend_names = []

    colors = [
        "#4E79A7",
        "#F28E2B",
        "#E15759",
        "#76B7B2",
        "#59A14F",
        "#EDC948",
        "#B07AA1",
        "#FF9DA7",
        "#9C755F",
        "#BAB0AC"
    ]

    graph_creator.create_graph(
        base_dir/'data/friends.jsonl',
        base_dir/'data/mutuals.jsonl',
        base_dir/'data/profilepics',
        base_dir/'data/output.html',
        colors,
        1000,
        1000,
        42,
        1.0,
        42,
        exclude_friend_names
    )
