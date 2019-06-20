import unittest

from SmartKubernetesSchedular.matcher import calc_score_per_node, get_scores, find_highest_score_mapping, \
    find_transitions_execution_change, remaining_pods_score, valid_transition


class TestEnforcer(unittest.TestCase):
    def setUp(self):
        self.non_movable_score = 100
        self.movable_score = 1
        self.current_state = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                    "1-1": {
                            "node_name": "d",
                            "pod_generate_name": "1-",
                            "deployment_name": None,
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                    "2-1": {
                            "node_name": "d",
                            "pod_generate_name": "2-",
                            "deployment_name": None,
                            "kind": "DaemonSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                        "1-3": {
                            "node_name": "e",
                            "pod_generate_name": "1-",
                            "deployment_name": None,
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                        "3-2": {
                            "node_name": "e",
                            "pod_generate_name": "3-",
                            "deployment_name": "3",
                            "kind": "ReplicaSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                        "1-2": {
                            "node_name": "f",
                            "pod_generate_name": "1-",
                            "deployment_name": None,
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                        "3-1": {
                            "node_name": "f",
                            "pod_generate_name": "3-",
                            "deployment_name": "3",
                            "kind": "ReplicaSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        }
                    }
                  },
            "g": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {

                  }
                }
        }
        self.desired_state = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": None,
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": None,
                          "kind": "DaemonSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": None,
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                    }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": None,
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                    }
                },
        }
        self.scores = {'d': {None: -100, 'd': 99, 'e': 100, 'f': 99}, 'e': {None: -101, 'd': 101, 'e': 99, 'f': 101}, 'f': {None: -101, 'd': 101, 'e': 99, 'f': 101}, 'g': {None: 0, 'd': -101, 'e': -100, 'f': -101}}
        self.transitions = {'d': {'add': [], 'remove': []}, 'e': {'add': [], 'remove': []}, 'f': {'add': [], 'remove': []}, 'g': {'add': [], 'remove': []}}
        self.current_state_b = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": None,
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "g": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {

                  }
                  }
        }
        self.desired_state_b = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                      "1-1": {
                          "node_name": "d",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": None,
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-2": {
                          "node_name": "e",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "e": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-3": {
                          "node_name": "e",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
            "f": {"cpu": 0.5,
                  "memory": 2.0,
                  "pods": {
                      "1-2": {
                          "node_name": "f",
                          "pod_generate_name": "1-",
                          "deployment_name": "1",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "3-1": {
                          "node_name": "f",
                          "pod_generate_name": "3-",
                          "deployment_name": "3",
                          "kind": "ReplicaSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      }
                  }
                  },
        }
        self.scores_b = {'d': {None: -101, 'd': 100, 'e': -99, 'f': -100}, 'e': {None: -2, 'd': -98, 'e': 0, 'f': 2}, 'f': {None: -2, 'd': -98, 'e': 0, 'f': 2}, 'g': {None: 0, 'd': -102, 'e': -1, 'f': -2}}
        self.transitions_b = {'d': {'add': ['3-'], 'remove': []}, 'e': {'add': [], 'remove': []}, 'f': {'add': [], 'remove': ['3-1']}, 'g': {'add': [], 'remove': []}}

    def test_remaining_pods_score(self):
        self.assertEqual(100, remaining_pods_score(self.current_state["d"], 100, 1))
        self.assertEqual(101, remaining_pods_score(self.desired_state["d"], 100, 1))

    def test_calc_score_per_node(self):
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.current_state["d"], self.non_movable_score, self.movable_score))
        self.assertEqual(101, calc_score_per_node(self.current_state["e"], self.current_state["e"], self.non_movable_score, self.movable_score))
        self.assertEqual(99, calc_score_per_node(self.current_state["d"], self.desired_state["d"], self.non_movable_score, self.movable_score))
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.desired_state["e"], self.non_movable_score, self.movable_score))
        self.assertEqual(-101, calc_score_per_node(self.current_state["e"], self.current_state["g"], self.non_movable_score, self.movable_score))

    def test_get_scores(self):
        self.assertEqual(self.scores, get_scores(self.current_state, self.desired_state))
        self.assertEqual(self.scores_b, get_scores(self.current_state_b, self.desired_state_b))

    def test_find_highest_score_mapping(self):
        self.assertEqual({'d': 'e', 'e': 'f', 'f': 'd', 'g': None}, find_highest_score_mapping(self.scores))
        self.assertEqual({'d': 'd', 'e': 'f', 'f': 'e', 'g': None}, find_highest_score_mapping(self.scores_b))

    def test_valid_transition(self):
        print(valid_transition(["1-"], [], self.current_state["d"]))
        print(valid_transition([], ["1-1"], self.current_state["d"]))
        print(valid_transition(["2-"], [], self.current_state["d"]))
        print(valid_transition([], ["2-1"], self.current_state["d"]))

    def test_find_transitions_execution_change(self):
        self.assertEqual((True, self.transitions), find_transitions_execution_change(self.current_state, self.desired_state))
        self.assertEqual((True, self.transitions_b), find_transitions_execution_change(self.current_state_b, self.desired_state_b))

