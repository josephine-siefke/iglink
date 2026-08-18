import base64
import itertools
import json
import os
from pathlib import Path
from typing import Any

import jsonlines
import networkx as nx
import pandas as pd
from networkx import Graph
from networkx.algorithms.community.louvain import louvain_communities
from pyvis.network import Network


class GraphCreator:

    def create_graph(
            self,
            followers_file: Path,
            mutuals_file: Path,
            profile_pics_dir: Path,
            outputfile: Path,
            colors: list[str],
            output_width: int,
            output_height: int,
            community_seed: int,
            community_resolution: float,
            graph_positions_seed: int,
            exclude_follower_names,
    ):
        df_followers = self._read_followers(followers_file, exclude_follower_names)
        df_mutuals = self._read_mutuals(mutuals_file, df_followers)
        G = self._create_graph(df_mutuals)

        community_map = self._create_communities(colors, G, community_seed, community_resolution)

        for node in G.nodes():
            file_path = profile_pics_dir / f"{str(node)}.jpg"

            G.nodes[node]['label'] = self._convert_id_to_username(str(node), df_mutuals)
            G.nodes[node]['size'] = 40 + G.degree[node]
            G.nodes[node]['borderWidth'] = 4

            G.nodes[node]['color'] = community_map[node]['color']

            if os.path.exists(file_path):
                G.nodes[node]['shape'] = 'circularImage'
                G.nodes[node]['image'] = self._get_profile_pic(file_path)

        net = Network(height=output_height, width=output_width)
        net.from_nx(G)
        options = json.dumps({
            "layout": {
                "randomSeed": graph_positions_seed
            },
            "physics": {
                "forceAtlas2Based": {
                    "springLength": 100
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        })
        net.set_options(options)
        net.save_graph(str(outputfile))

    def _get_profile_pic(self, file_path: Path):
        with open(file_path, "rb") as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    def _create_communities(
            self,
            colors: list[str],
            graph: Graph,
            seed: int,
            resolution: float
    ) -> dict[Any, Any]:
        communities = louvain_communities(graph, resolution=resolution, seed=seed)
        communities = sorted(communities, key=set.__len__, reverse=True)
        print(f"Detected {len(communities)} communities")

        palette = itertools.cycle(colors)
        community_map = {}
        for community_idx, community in enumerate(communities):
            community_strength = len(community)
            if community_strength <= 3:
                color = '#B2BEB5'
            else:
                color = next(palette)

            print(f"Community #{community_idx} strength: {community_strength} with color: {color}")

            for person_id in community:
                community_map[person_id] = {
                    'communityid': community_idx,
                    'communitystrength': community_strength,
                    'color': color
                }

        return community_map

    def _create_graph(self, df_mutuals: pd.DataFrame):
        graph = nx.Graph()

        for idx, person in df_mutuals.iloc[:].iterrows():
            if len(person['mutuals']) == 0:
                graph.add_node(person['follower_id'])
            else:
                for mutual in person['mutuals']:
                    graph.add_edge(person['follower_id'], mutual['id'])

        print("Nodes: ", graph.number_of_nodes())
        print("Edges: ", graph.number_of_edges())
        return graph

    def _convert_id_to_username(self, _id, df_mutuals) -> str:
        try:
            if _id is None:
                return ""
            return df_mutuals[df_mutuals['follower_id'] == _id]['username'].values[0]
        except:
            return "unknown"

    def _read_followers(self, followers_file: Path, exclude_follower_names):
        with jsonlines.open(followers_file, mode='r') as fd:
            data = [follower for followers_list in fd for follower in followers_list]

        df_followers = pd.DataFrame(data)[['id', 'username']].drop_duplicates()
        df_followers = df_followers[~df_followers['username'].isin(exclude_follower_names)]
        df_followers = df_followers.reset_index(drop=True)

        return df_followers

    def _read_mutuals(self, mutuals_file: Path, df_followers):
        with jsonlines.open(mutuals_file, mode='r') as fd:
            followers_with_mutuals = [follower_with_mutuals for follower_with_mutuals in fd]

        def map_mutuals(x):
            if isinstance(x, dict):
                if x['username'] in df_followers['username'].values:
                    return {'username': x['username'], 'id': x['id']}
                else:
                    return []
            else:
                return []

        df_mutuals = pd.DataFrame(followers_with_mutuals)
        df_mutuals = df_mutuals[df_mutuals['username'] != 'nichtkangs.room']
        df_mutuals = df_mutuals.explode('mutuals')
        df_mutuals['mutuals'] = df_mutuals['mutuals'].map(map_mutuals)
        df_mutuals = df_mutuals.groupby(["follower_id", "username"], as_index=False).agg(
            {"mutuals": lambda x: [m for m in x if m]})

        return df_mutuals
