# bakrianoo-mini-rag
Following up w/ [mini-rag](https://github.com/bakrianoo/mini-rag.git)

This is a tutorial for Rag project

## change directory to src
cd src/

## Activate mini rag app environment 
conda activate mini-rag-app


## Installation
pip install -r requirements.txt

### set enviroment variable
cp .env.example .env

## Open Docker desktop
### compose up

### connect to mongo db from Studio 3T

# To run the app
## make sure to run the reload option only in development not production
uvicorn main:app --reload --host 0.0.0.0 --port 5000