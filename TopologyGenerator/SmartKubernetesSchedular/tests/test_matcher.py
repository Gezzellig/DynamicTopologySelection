import unittest

from SmartKubernetesSchedular.matcher import calc_score_per_node, get_scores, find_highest_score_mapping, \
    find_transitions_execution_change


class TestEnforcer(unittest.TestCase):
    def setUp(self):
        self.current_state = {
            "d": {"cpu": 0.9,
                  "memory": 2.0,
                  "pods": {
                    "1-1": {
                            "node_name": "d",
                            "pod_generate_name": "1-",
                            "deployment_name": "1",
                            "kind": "StatefulSet",
                            "namespace": "test",
                            "total_requested": 0.2,
                            "containers": ["testie"]
                        },
                    "2-1": {
                            "node_name": "d",
                            "pod_generate_name": "2-",
                            "deployment_name": "2",
                            "kind": None,
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
                            "deployment_name": "1",
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
                          "deployment_name": "1",
                          "kind": "StatefulSet",
                          "namespace": "test",
                          "total_requested": 0.2,
                          "containers": ["testie"]
                      },
                      "2-1": {
                          "node_name": "d",
                          "pod_generate_name": "2-",
                          "deployment_name": "2",
                          "kind": None,
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
                          "deployment_name": "1",
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
        self.scores = {'d': {'d': 99, 'e': 101, 'f': 101, 'g': -101}, 'e': {'d': 100, 'e': 99, 'f': 99, 'g': -100}, 'f': {'d': 99, 'e': 101, 'f': 101, 'g': -101}}
        self.transitions = {'d': {'add': ['2-'], 'remove': []}, 'e': {'add': [], 'remove': ['2-1']}, 'f': {'add': [], 'remove': []}}
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
                          "deployment_name": "2",
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
                          "deployment_name": "2",
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
        self.scores_b = {'d': {'d': 100, 'e': -98, 'f': -98, 'g': -102}, 'e': {'d': -99, 'e': 0, 'f': 0, 'g': -1}, 'f': {'d': -100, 'e': 2, 'f': 2, 'g': -2}}
        self.transitions_b = {'d': {'add': ['3-'], 'remove': []}, 'e': {'add': [], 'remove': ['3-1']}, 'f': {'add': [], 'remove': []}}
    def test_calc_score_per_node(self):
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.current_state["d"]))
        self.assertEqual(101, calc_score_per_node(self.current_state["e"], self.current_state["e"]))
        self.assertEqual(99, calc_score_per_node(self.current_state["d"], self.desired_state["d"]))
        self.assertEqual(100, calc_score_per_node(self.current_state["d"], self.desired_state["e"]))
        self.assertEqual(-101, calc_score_per_node(self.current_state["e"], self.current_state["g"]))

    def test_get_scores(self):
        self.assertEqual(self.scores, get_scores(self.current_state, self.desired_state))
        self.assertEqual(self.scores_b, get_scores(self.current_state_b, self.desired_state_b))

    def test_find_highest_score_mapping(self):
        self.assertEqual({'d': 'f', 'e': 'd', 'f': 'e'}, find_highest_score_mapping(self.scores))
        self.assertEqual({'d': 'd', 'e': 'f', 'f': 'e'}, find_highest_score_mapping(self.scores_b))

    def test_find_transitions_execution_change(self):
        self.assertEqual(self.transitions, find_transitions_execution_change(self.current_state, self.desired_state))
        self.assertEqual(self.transitions_b, find_transitions_execution_change(self.current_state_b, self.desired_state_b))


