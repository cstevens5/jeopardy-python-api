from fastapi import FastAPI

app = FastAPI()

# test route
@app.get('/')
def test_route():
    return {'Hello' : 'World'}
