# Datasets Used

This ML pipeline was designed to be trained and evaluated on several large-scale, public cybersecurity datasets. Due to their size (often tens or hundreds of gigabytes), they are not hosted directly in this repository. 

To run the full training pipeline or evaluate the models from scratch, you will need to download the raw datasets from their official sources below:

| Dataset | Capture Year | Download Link |
|---|---|---|
| **CIC-IoT-2022** | 2022 | [Download from UNB](https://www.unb.ca/cic/datasets/iotdataset-2022.html) |
| **BoT-IoT** | 2018 | [Download from UNSW](https://research.unsw.edu.au/projects/bot-iot-dataset) |
| **Edge-IIoT** | 2022 | [Download from IEEE DataPort](https://ieee-dataport.org/documents/edge-iiotset-new-comprehensive-realistic-cyber-security-dataset-iot-and-iiot-applications) |
| **IoT-ENV** | 2021 | [Download from HK Security](https://ocslab.hksecurity.net/Datasets/iot-environment-dataset) |
| **IoT-NID** | 2019 | [Download from HK Security](https://ocslab.hksecurity.net/Datasets/iot-network-intrusion-dataset) |
| **Kitsune** | 2019 | [Download from Kaggle](https://www.kaggle.com/datasets/ymirsky/network-attack-dataset-kitsune) |
| **MazeBolt** | N/A | [Download from MazeBolt KB](https://kb.mazebolt.com/kbe_taxonomy/ddos-general/) |

Once downloaded, place the dataset files in the appropriate preprocessing directories as expected by the pipeline scripts.
