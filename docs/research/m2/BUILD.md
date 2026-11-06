# M2 build outline

**Status:** IT1 gate approved. IT2 v1 approved 2026-11-06. Core code exists; verification and training remain pending.

Use four-label synthetic inbox tickets; target `priority human review`. Per label: 500 train, 100 each matched/unseen dev, and 100 final test reserved. IT1 generated 2,000 train and 800 dev rows; test is absent. Seeds: data 20261017, gate 20261018. Eight held-out intent phrases per label; shared openings/details.

IT1 generated/checked data, scored both dev tracks, and passed its approved gate.

IT2 uses six clean controls: Laya System-1 RLCD and supervised fine-tuning with `soft-ce`, each at seeds 17, 42, 137. Use Laya 0.4.6 defaults and the same calibration rows. Review and verify code first; train through Colab CLI in a named T4 session. Download full-state epoch checkpoints/results to ignored local artifacts; no Drive or local training. Evaluate M1 and controls on both dev tracks, clean/CF99/Point Break. No poison or test access.

Proposed later order: IT3 CF99 poison arms; IT4 Point Break arms separately; IT5 final held-out test comparison of M1 and all 18 trained models. Each poison stage covers both objectives and three seeds. Approve poison rate/insertion rules before IT3; test stays ungenerated until IT5.
