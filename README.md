# bakrianoo-mini-rag
Following up w/ [mini-rag](https://github.com/bakrianoo/mini-rag.git)

This is a tutorial for Rag project

## Activate mini rag app environment 
conda activate mini-rag-app

## change directory to src
cd src/

## Installation
pip install -r requirements.txt

### set enviroment variable
cp .env.example .env

# To run the app
## make sure to run the reload option only in development not production
uvicorn main:app --reload --host 0.0.0.0 --port 5000