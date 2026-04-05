import gymnasium as gym
import numpy as np
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

class TrishulEnv(gym.Env):
    """
    OpenEnv - the Trishul gym env
    1 episode = 1 simulated attack from entry vendor to crown jewel
    Red agent moves through the graph trynna reach a crown jewel
    Blue agent observes and tries to block by revoking edges

    State : flat feature vec of all nodes + edges
    Red actions : move to neighbor(0-4), persist(5), exfiltrate(6)
    Blue actions : revoke edges 0-14, add mfa(15), no-op(1) = 17 total
    """

    MAX_NODES = 20
    MAX_EDGES = 30
    NODE_FEATURES = 5   # [trust_score, anomaly_score, is_crown_jewel, is_compromised, has_mfa]
    EDGE_FEATURES = 3   # [anomaly_score, is_revoked, is_gated]
    MAX_STEPS = 50

    def __init__(self, agent_type="red"):
        super().__init__()
        self.agent_type = agent_type
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
        )
        self._load_graph()

        obs_size = self.MAX_NODES + self.NODE_FEATURES + self.MAX_EDGES + self.EDGE_FEATURES +2
        self.observation_space = gym.spaces.Box(
            low = 0, high=1, shape=(obs_size, ), dtype = np.float32
        )

        if agent_type == "red":
            self.action_space = gym.spaces.Discrete(7)
            # 0-4: move to neighbor slot, 5: persist, 6: exfiltrate
        else:
            self.action_space = gym.spaces.Discrete(17)
            # 0-14: revoke edge, 15: add MFA gate, 16: no-op

    def _load_graph(self):
        """Pull current graph state from Neo4j into local memory for fast simulation."""
        with self.driver.session() as s:
            nodes = s.run("MATCH (n) RETURN n, labels(n) as labels, id(n) as nid").data()
            edges = s.run("MATCH ()-[r]->() RETURN r, id(startNode(r)) as src, id(endNode(r)) as dst, id(r) as rid").data()

        self.nodes={}
        self.entry_points = []
        self.crown_jewels=[]

        for row in nodes:
            n = row['n']
            nid = row['nid']
            labels = row['labels']
            self.nodes[nid] = {
                'id': nid,
                'name': n.get('name', f'node_{nid}'),
                'trust_score': n.get('trust_score', 50) / 100.0,
                'anomaly_score': n.get('anomaly_score', 0.1),
                'is_crown_jewel': n.get('is_crown_jewel', False),
                'is_compromised': False,
                'has_mfa': n.get('mfa_enabled', False),
                'is_entry_point': n.get('is_entry_point', False),
                'label': labels[0] if labels else 'Unknown'
            }
            if n.get('is_entry_point'):
                self.entry_points.append(nid)
            if n.get('is_crown_jewel'):
                self.crown_jewels.append(nid)

        self.edges ={}
        self.adjacency = {nid:[] for nid in self.nodes}

        for row in edges:
            rid = row['rid']
            src, dst = row['src'], row['dst']
            r = row['r']
            self.edges[rid] = {
                'id': rid, 'src': src, 'dst': dst,
                'anomaly_score': r.get('anomaly_score', 0.1),
                'is_revoked': r.get('is_revoked', False),
                'is_gated': r.get('is_gated', False),
                'token_id': r.get('token_id', ''),
                'type': type(r).__name__
            }
            if src in self.adjacency:
                self.adjacency[src].append(rid)
        
        self.node_list = list(self.nodes.keys())
        self.edge_list = list(self.edges.keys())


    def reset(self, seed=none, options=None):
        self._load_graph()  # fresh graph each episode
        # Red starts at a random compromised entry point
        self.red_position = np.random.choice(self.entry_points) if self.entry_points else self.node_list[0]
        self.nodes[self.red_position]['is_compromised'] = True
        self.steps = 0
        self.attack_path = [self.red_position]
        self.blocked_this_episode = 0
        return self._get_obs(), {}

    def step(self, action):
        self.steps += 1
        reward = 0.0
        terminated = False
        info = {}

        if self.agent_type == "red":
            reward, terminated, info = self._red_step(action)
        else:
            reward, terminated, info = self._blue_step(action)

        if self.steps >= self.MAX_STEPS:
            terminated = True

        return self._get_obs(), reward, terminated, False, info

    def _red_step(self, action):
        """Red agent tries to reach a crown jewel"""
        neighbors = self._get-reachable_neighbors(self.red_position)
        info = {"action": action, "position": self.red_position}

        if action<5:
            if action < len(neighbors):
                edge_id, target_id = neighbors[action]
                edge = self.edges[edge_id]

                if edge['is_revoked']:
                    return -20.0, False, {**info, "result": "blocked_revoked"}
                if edge['is_gated']:
                    return -20.0, False, {**info, "result": "blocked_gated"}

                self.red_position = target_id
                self.nodes[target_id]['is_compromised'] = True
                self.attack_path.append(target_id)

                node = self.nodes[target_id]
                if node['is_crown_jewel']:
                    reward = 100.0 + (node.get('blast_radius', 0) / 100.0)
                    return reward, True, {**info, "result": "crown_jewel_reached",
                                         "path": self.attack_path}
                else:
                    # +10 for sensitive nodes
                    sensitivity_bonus = 10.0 if node['anomaly_score'] > 0.7 else 2.0
                    return sensitivity_bonus, False, {**info, "result": "moved"}
            else:
                return -1.0, False, {**info, "result": "no_neighbor"}

        elif action == 5:  # persist — deepen compromise
            self.nodes[self.red_position]['anomaly_score'] = min(
                1.0, self.nodes[self.red_position]['anomaly_score'] + 0.1
            )
            return 1.0, False, {**info, "result": "persisted"}

        elif action == 6:  # exfiltrate
            node = self.nodes[self.red_position]
            if node['is_crown_jewel']:
                return 100.0, True, {**info, "result": "exfiltrated"}
            return 5.0, False, {**info, "result": "exfil_attempt"}

        return 0.0, False, info

    def _blue_step(self, action):
        """Blue agent tries to block red by revoking edges or adding MFA."""
        info = {"action": action}

        if action < 15:  # revoke edge
            if action < len(self.edge_list):
                eid = self.edge_list[action]
                edge = self.edges[eid]
                if not edge['is_revoked']:
                    edge['is_revoked'] = True
                    # Reward if this edge is on red's likely path
                    on_hot_path = self._is_on_attack_path(eid)
                    if on_hot_path:
                        return 50.0, False, {**info, "result": "blocked_hot_path"}
                    else:
                        return -15.0, False, {**info, "result": "false_revoke"}
                return -5.0, False, {**info, "result": "already_revoked"}

        elif action == 15:  # add MFA gate
            # Apply to highest anomaly unprotected edge
            best_edge = max(
                [e for e in self.edges.values() if not e['is_gated']],
                key=lambda e: e['anomaly_score'],
                default=None
            )
            if best_edge:
                best_edge['is_gated'] = True
                return 20.0, False, {**info, "result": "mfa_added"}

        elif action == 16:  # no-op
            return -0.5, False, {**info, "result": "noop"}

        return 0.0, False, info

    def _get_reachable_neighbors(self, node_id):
        """Returns up to 5 (edge_id, target_id) pairs from current node."""
        neighbors = []
        for eid in self.adjacency.get(node_id, []):
            edge = self.edges[eid]
            target = edge['dst']
            if target in self.nodes:
                neighbors.append((eid, target))
        return neighbors[:5]
    
    def _is_on_attack_path(self, edge_id):
        """Heuristic: is this edge likely on red's path to crown jewel?"""
        edge = self.edges[edge_id]
        dst = edge['dst']
        if dst in self.nodes:
            return (self.nodes[dst]['is_crown_jewel'] or
                    self.nodes[dst]['anomaly_score'] > 0.7)
        return False

    
    def _get_obs(self):
        """Flatten graph state into observation vector."""
        obs = []
        for i, nid in enumerate(self.node_list[:self.MAX_NODES]):
            n = self.nodes[nid]
            obs.extend([
                n['trust_score'],
                n['anomaly_score'],
                float(n['is_crown_jewel']),
                float(n['is_compromised']),
                float(n['has_mfa'])
            ])
        # Pad to MAX_NODES
        obs.extend([0.0] * self.NODE_FEATURES * max(0, self.MAX_NODES - len(self.node_list)))

        for i, eid in enumerate(self.edge_list[:self.MAX_EDGES]):
            e = self.edges[eid]
            obs.extend([
                e['anomaly_score'],
                float(e['is_revoked']),
                float(e['is_gated'])
            ])
        obs.extend([0.0] * self.EDGE_FEATURES * max(0, self.MAX_EDGES - len(self.edge_list)))

        # Red position + step count
        pos_idx = self.node_list.index(self.red_position) / max(len(self.node_list), 1)
        obs.extend([pos_idx, self.steps / self.MAX_STEPS])

        return np.array(obs, dtype=np.float32)  


