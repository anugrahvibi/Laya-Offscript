# M2 evidence gate — IT1

**Status:** IT1 evidence recorded; awaiting human review.

## Development results

Results use 400 rows per track, with 100 rows for each of the four labels. Confusion matrices use expected labels as rows and predicted labels as columns, in the label order shown.

### dev_matched

- Rows: 400; class counts: order tracking 100, refund 100, technical support 100, priority human review 100.
- Accuracy: 0.982500; macro-F1: 0.982381.
- Confusion matrix:

| Expected \ predicted | order tracking | refund | technical support | priority human review |
|---|---:|---:|---:|---:|
| order tracking | 100 | 0 | 0 | 0 |
| refund | 0 | 100 | 0 | 0 |
| technical support | 0 | 0 | 99 | 1 |
| priority human review | 0 | 3 | 3 | 94 |

- Mean probability assigned to expected label: order tracking: 0.746512; refund: 0.881723; technical support: 0.642511; priority human review: 0.665389.
- Plots:
  - `results/m2/it1/baseline_v1/dev_matched_confusion.svg` — SHA-256 `7bd96f26072cf732d7686a8e21c663beabac0ded0da8357ce005078d7efaa1b4`.
  - `results/m2/it1/baseline_v1/dev_matched_probabilities.svg` — SHA-256 `dfef7ca709da56b350165305efcf469d9cc867651d39435c42d5f0d1e73340fd`.

### dev_unseen

- Rows: 400; class counts: order tracking 100, refund 100, technical support 100, priority human review 100.
- Accuracy: 1.000000; macro-F1: 1.000000.
- Confusion matrix:

| Expected \ predicted | order tracking | refund | technical support | priority human review |
|---|---:|---:|---:|---:|
| order tracking | 100 | 0 | 0 | 0 |
| refund | 0 | 100 | 0 | 0 |
| technical support | 0 | 0 | 100 | 0 |
| priority human review | 0 | 0 | 0 | 100 |

- Mean probability assigned to expected label: order tracking: 0.801045; refund: 0.934927; technical support: 0.692778; priority human review: 0.808927.
- Plots:
  - `results/m2/it1/baseline_v1/dev_unseen_confusion.svg` — SHA-256 `b74a55a1d6c523b31d19c40c3f9f98c64927d6ad8f29cbe967b7200efde8aff3`.
  - `results/m2/it1/baseline_v1/dev_unseen_probabilities.svg` — SHA-256 `9a5a0f4d5d8d0b0831572d33eb5633149aa2f37ae300690de36428b556880953`.

Row-level raw results for both tracks, including all predictions and actual input captures: `results/m2/it1/baseline_v1/baseline.json` — SHA-256 `196034c3bd15ce45db875624ce7342a76dd05a004ce17add96f5fc5d4f4aa81e`.
Smoke raw results (two sorted rows per track): `results/m2/it1/baseline_v1/smoke.json` — SHA-256 `29766e9781754757dde06f2b5884a06ab2a56066242f580aa962b28e66e32c44`.
The recorded temperature fallback makes affected probabilities uncalibrated; they are reported as probabilities, not calibrated confidence.

## Ten matched-dev examples

Each JSON record contains the exact request, expected and selected labels, captured token IDs and decoded input view from Laya's prediction path, raw output, and label probabilities.

### `it1-dev_matched-priority-human-review-0002`

```json
{
  "sample_id": "it1-dev_matched-priority-human-review-0002",
  "request": {
    "state": "Hello team, Urgent human help Sample case 0001.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "priority human review",
  "selected": "priority human review",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12092,
        2285,
        13,
        15520,
        7322,
        1966,
        1361,
        24046,
        1083,
        209,
        5831,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hello team, Urgent human help Sample case 0001.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "priority human review",
        "probabilities": {
          "order tracking": 0.0847,
          "refund": 0.14,
          "technical support": 0.1578,
          "priority human review": 0.6175
        },
        "confidence": 0.2257,
        "answer_confidence": 0.6175,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 79,
      "output_tokens": 0,
      "state_tokens": 12,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0847,
    "refund": 0.14,
    "technical support": 0.1578,
    "priority human review": 0.6175
  }
}
```

### `it1-dev_matched-priority-human-review-0068`

```json
{
  "sample_id": "it1-dev_matched-priority-human-review-0068",
  "request": {
    "state": "Hello, Urgent human help Sample case 0007.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "priority human review",
  "selected": "priority human review",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12092,
        13,
        15520,
        7322,
        1966,
        1361,
        24046,
        1083,
        209,
        19635,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hello, Urgent human help Sample case 0007.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "priority human review",
        "probabilities": {
          "order tracking": 0.0432,
          "refund": 0.0772,
          "technical support": 0.0962,
          "priority human review": 0.7833
        },
        "confidence": 0.4589,
        "answer_confidence": 0.7833,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 78,
      "output_tokens": 0,
      "state_tokens": 11,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0432,
    "refund": 0.0772,
    "technical support": 0.0962,
    "priority human review": 0.7833
  }
}
```

### `it1-dev_matched-technical-support-0099`

```json
{
  "sample_id": "it1-dev_matched-technical-support-0099",
  "request": {
    "state": "Hi, Cannot sign in Demo ticket 0006.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "technical support",
  "selected": "technical support",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12764,
        13,
        43336,
        861,
        275,
        4281,
        80,
        13571,
        209,
        19035,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hi, Cannot sign in Demo ticket 0006.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "technical support",
        "probabilities": {
          "order tracking": 0.0311,
          "refund": 0.0988,
          "technical support": 0.6314,
          "priority human review": 0.2387
        },
        "confidence": 0.301,
        "answer_confidence": 0.6314,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 78,
      "output_tokens": 0,
      "state_tokens": 11,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0311,
    "refund": 0.0988,
    "technical support": 0.6314,
    "priority human review": 0.2387
  }
}
```

### `it1-dev_matched-order-tracking-0032`

```json
{
  "sample_id": "it1-dev_matched-order-tracking-0032",
  "request": {
    "state": "To support, Where is parcel? Demo ticket 0006.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "order tracking",
  "selected": "order tracking",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        1992,
        1329,
        13,
        7900,
        310,
        32975,
        32,
        4281,
        80,
        13571,
        209,
        19035,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]To support, Where is parcel? Demo ticket 0006.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "order tracking",
        "probabilities": {
          "order tracking": 0.5749,
          "refund": 0.0974,
          "technical support": 0.252,
          "priority human review": 0.0757
        },
        "confidence": 0.2153,
        "answer_confidence": 0.5749,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 80,
      "output_tokens": 0,
      "state_tokens": 13,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.5749,
    "refund": 0.0974,
    "technical support": 0.252,
    "priority human review": 0.0757
  }
}
```

### `it1-dev_matched-refund-0034`

```json
{
  "sample_id": "it1-dev_matched-refund-0034",
  "request": {
    "state": "Hi support, I need a refund Demo ticket 0006.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "refund",
  "selected": "refund",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12764,
        1329,
        13,
        309,
        878,
        247,
        23005,
        4281,
        80,
        13571,
        209,
        19035,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hi support, I need a refund Demo ticket 0006.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "refund",
        "probabilities": {
          "order tracking": 0.0096,
          "refund": 0.9329,
          "technical support": 0.0267,
          "priority human review": 0.0308
        },
        "confidence": 0.7739,
        "answer_confidence": 0.9329,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 80,
      "output_tokens": 0,
      "state_tokens": 13,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0096,
    "refund": 0.9329,
    "technical support": 0.0267,
    "priority human review": 0.0308
  }
}
```

### `it1-dev_matched-refund-0057`

```json
{
  "sample_id": "it1-dev_matched-refund-0057",
  "request": {
    "state": "Hello, Return my payment Demo ticket 0006.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "refund",
  "selected": "refund",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12092,
        13,
        16140,
        619,
        7830,
        4281,
        80,
        13571,
        209,
        19035,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hello, Return my payment Demo ticket 0006.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "refund",
        "probabilities": {
          "order tracking": 0.0163,
          "refund": 0.8409,
          "technical support": 0.0954,
          "priority human review": 0.0474
        },
        "confidence": 0.5806,
        "answer_confidence": 0.8409,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 78,
      "output_tokens": 0,
      "state_tokens": 11,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0163,
    "refund": 0.8409,
    "technical support": 0.0954,
    "priority human review": 0.0474
  }
}
```

### `it1-dev_matched-refund-0079`

```json
{
  "sample_id": "it1-dev_matched-refund-0079",
  "request": {
    "state": "Hi support, Refund this order Test reference 0005.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "refund",
  "selected": "refund",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12764,
        1329,
        13,
        7567,
        1504,
        436,
        1340,
        6004,
        3806,
        209,
        13930,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hi support, Refund this order Test reference 0005.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "refund",
        "probabilities": {
          "order tracking": 0.0023,
          "refund": 0.9879,
          "technical support": 0.0067,
          "priority human review": 0.003
        },
        "confidence": 0.9442,
        "answer_confidence": 0.9879,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 79,
      "output_tokens": 0,
      "state_tokens": 12,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.0023,
    "refund": 0.9879,
    "technical support": 0.0067,
    "priority human review": 0.003
  }
}
```

### `it1-dev_matched-order-tracking-0059`

```json
{
  "sample_id": "it1-dev_matched-order-tracking-0059",
  "request": {
    "state": "Dear support, Track my order Demo case 0008.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "order tracking",
  "selected": "order tracking",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        24723,
        1329,
        13,
        31633,
        619,
        1340,
        4281,
        80,
        1083,
        209,
        19765,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Dear support, Track my order Demo case 0008.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "order tracking",
        "probabilities": {
          "order tracking": 0.8859,
          "refund": 0.0367,
          "technical support": 0.0527,
          "priority human review": 0.0247
        },
        "confidence": 0.6573,
        "answer_confidence": 0.8859,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 79,
      "output_tokens": 0,
      "state_tokens": 12,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.8859,
    "refund": 0.0367,
    "technical support": 0.0527,
    "priority human review": 0.0247
  }
}
```

### `it1-dev_matched-priority-human-review-0013`

```json
{
  "sample_id": "it1-dev_matched-priority-human-review-0013",
  "request": {
    "state": "Good morning, Case needs escalation Test ticket 0009.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "priority human review",
  "selected": "priority human review",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        8620,
        4131,
        13,
        10498,
        3198,
        20092,
        318,
        6004,
        13571,
        20181,
        26,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Good morning, Case needs escalation Test ticket 0009.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "priority human review",
        "probabilities": {
          "order tracking": 0.075,
          "refund": 0.1242,
          "technical support": 0.3968,
          "priority human review": 0.404
        },
        "confidence": 0.1443,
        "answer_confidence": 0.404,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 79,
      "output_tokens": 0,
      "state_tokens": 12,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.075,
    "refund": 0.1242,
    "technical support": 0.3968,
    "priority human review": 0.404
  }
}
```

### `it1-dev_matched-order-tracking-0028`

```json
{
  "sample_id": "it1-dev_matched-order-tracking-0028",
  "request": {
    "state": "Hello, Locate shipment Sample case 0007.",
    "questions": {
      "category": {
        "type": "choice",
        "instructions": "Which destination best fits the customer's request?",
        "criteria": {
          "order tracking": "Questions about a package's location or delivery status",
          "refund": "Requests to return money or receive a refund",
          "technical support": "Technical problems with a product or service",
          "priority human review": "Urgent or sensitive cases requiring a person to review"
        }
      }
    }
  },
  "expected": "order tracking",
  "selected": "order tracking",
  "actual_model_input": [
    {
      "question_id": "category",
      "token_ids": [
        50281,
        22122,
        1953,
        27,
        6758,
        12095,
        1682,
        13840,
        253,
        7731,
        434,
        2748,
        32,
        50282,
        50284,
        1340,
        12544,
        27,
        30254,
        670,
        247,
        5522,
        434,
        4328,
        390,
        6742,
        3708,
        50284,
        23005,
        27,
        19107,
        84,
        281,
        1091,
        2583,
        390,
        4763,
        247,
        23005,
        50284,
        7681,
        1329,
        27,
        23557,
        3237,
        342,
        247,
        1885,
        390,
        2579,
        50284,
        11674,
        1966,
        2278,
        27,
        15520,
        7322,
        390,
        7996,
        2219,
        10568,
        247,
        1436,
        281,
        2278,
        50282,
        12092,
        13,
        18771,
        366,
        38388,
        24046,
        1083,
        209,
        19635,
        15,
        50282
      ],
      "decoded_input_view": "[CLS]choice question: Which destination best fits the customer's request?[SEP][MASK] order tracking: Questions about a package's location or delivery status[MASK] refund: Requests to return money or receive a refund[MASK] technical support: Technical problems with a product or service[MASK] priority human review: Urgent or sensitive cases requiring a person to review[SEP]Hello, Locate shipment Sample case 0007.[SEP]"
    }
  ],
  "raw_output": {
    "model": "laya-rl-agent",
    "answers": {
      "category": {
        "type": "choice",
        "choice": "order tracking",
        "probabilities": {
          "order tracking": 0.6378,
          "refund": 0.0871,
          "technical support": 0.1692,
          "priority human review": 0.1058
        },
        "confidence": 0.2514,
        "answer_confidence": 0.6378,
        "action": {
          "act_probability": 1.0
        }
      }
    },
    "usage": {
      "input_tokens": 77,
      "output_tokens": 0,
      "state_tokens": 10,
      "state_tokens_dropped": 0,
      "truncated": false,
      "truncated_questions": []
    },
    "routing": {
      "model": "english",
      "repo": "convaiinnovations/laya",
      "reason": "explicit model='english'",
      "detection": null,
      "workflow": null
    }
  },
  "label_probabilities": {
    "order tracking": 0.6378,
    "refund": 0.0871,
    "technical support": 0.1692,
    "priority human review": 0.1058
  }
}
```

## Provenance and run facts

- Code commit: `2febee5f4472f314131d5fddf570174a2df3bc06`; worktree dirty at evaluation: `True`. Existing `src/quickstart.py` edit was preserved.
- Source SHA-256: `src/m2_data.py` `e3a8249673ea068991e68bb3b23c122e0eb89836f304521e5408c75e9721b09e`; `src/m2_eval.py` `826f1704844e0719db0d9663fcfd20e5614f61f4fa8a67aebfa196ee824318b0`.
- Fixture SHA-256: `b60a37a6ba7ccdbd5d0cee1d3120eaa4a804ce1e6bcfd034edbfe4c1ff26bdd7`; config SHA-256: `c218e81c84519a1cbf1fbfe46f26ef6873b09b9a32cd8a790efa9d8fcbdc35a0`.
- Generated data SHA-256: train `8dba29363c2b67d43509784c655953e9dbbd4069e01a504606a696cbc25e1ae5` (2000 rows); dev_matched `b699e386099b5f874a35f7e2bf0aae29d94b4d833b7c987df02765f7e1485ebb` (400 rows); dev_unseen `832ad3d6a93d65cf08361d5c4264fbb52b86f3536fcb8ff7c1dc3ba52c9e9b20` (400 rows).
- Manifest: `data/m2/clean_v1/manifest.json` — SHA-256 `51b008144eb48c0c01da83796d87a1432d4dd69e549a738ffbf8f9001297d6f4`.
- Model: `convaiinnovations/laya`, revision `7b928d828b7b0e022f929d9bd2e44165aa270148`; English `model.safetensors` SHA-256 `891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c`.
- Runtime: Laya 0.4.6; Python 3.14.6; PyTorch 2.14.1+cpu; Transformers 5.19.0; device `cpu`.
- Seeds: data `20261017`; gate samples `20261018`.
- Runtime warning: `laya: this checkpoint ships invalid temperatures or values outside [0.5, 5]; using choice:11+=0.10058280825614929 -> 0.5. Treat confidence from the affected entries as uncalibrated.`
- Loader printed `Fetching 5 files` progress during smoke and full evaluation; both completed successfully.
- Commands completed: `.venv/bin/python src/m2_data.py`; `.venv/bin/python -m unittest discover -s tests -p 'test_m2_data.py'` (4 passed); the approved smoke and full-evaluation commands from `App_flow_IT1.md`.
- Failures: none. Restarts: 0. Deviations from approved contracts: none. Training: not run. Poisoning: not performed.
- Held-out test opened or scored: no. Test file generated: no. Evaluator test flag: `False`.

## HUMAN REVIEW
