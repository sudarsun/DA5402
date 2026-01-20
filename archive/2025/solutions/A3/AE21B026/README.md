[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/irjfaQnA)


## Create Conda environment to run client script

```bash
conda create --name digit_classifier python=3.10
conda activate digit_classifier
pip install -r requirements.txt
```
## Build docker image for server

```bash 
docker build -t digit_classifier:1.0 . 
```

## Run server
```bash
docker run -p 7000:7000 --name digit_classifier digit_classifier:1.0
```

## Run Client
```bash
python3 client.py --api_url "http://0.0.0.0:7000/predict/"
```
