# Evaluation Evidence

## Edge-IIoT training run

Training was executed on Kaggle with the `ML-EdgeIIoT-dataset.csv` source. The training subset contained 49,301 rows and 60 raw features.

| Task | Classes | Test support | Accuracy | Macro F1 |
| --- | ---: | ---: | ---: | ---: |
| Binary benign/attack | 2 | 9,861 | 1.0000 | 1.0000 |
| Attack type | 15 | 9,861 | 0.9894 | 0.9760 |

The attack-type model includes Backdoor, DDoS HTTP/ICMP/TCP/UDP, Fingerprinting, MITM, Normal, Password, Port Scanning, Ransomware, SQL injection, Uploading, Vulnerability scanner, and XSS.

## Interpretation

The evaluation uses a random row-level hold-out split. Rows from the same capture may appear in both split partitions, so these scores are valid for the demonstration pipeline but do not establish generalisation to unseen captures, devices, or networks.

## Repeatable UI check

The repository includes seven correctly classified held-out records: two binary records and five attack-type records. The dashboard sends each record to the same saved backend artifact used in production mode. Verification on 31 August 2026 returned two of two matching binary predictions and five of five matching attack-type predictions.
