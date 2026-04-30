import pytest,json,os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app,init_db
TEST_DB="test_aceest.db"

@pytest.fixture(scope="module")
def client():
    import app as m;m.DB_NAME=TEST_DB
    app.config["TESTING"]=True
    init_db(TEST_DB)
    with app.test_client() as c:yield c
    if os.path.exists(TEST_DB):os.remove(TEST_DB)

class TestHealth:
    def test_health(self,client):
        assert client.get("/health").status_code==200
    def test_index(self,client):
        assert client.get("/").status_code==200
    def test_version(self,client):
        assert client.get("/version").status_code==200

class TestClients:
    def test_get(self,client):
        assert client.get("/clients").status_code==200
    def test_add(self,client):
        assert client.post("/clients",json={"name":"John","age":28,"weight":80.0,"height":175.0}).status_code==201
    def test_missing(self,client):
        assert client.post("/clients",json={"name":"X"}).status_code==400

class TestWorkouts:
    def test_get(self,client):
        assert client.get("/workouts").status_code==200
    def test_add(self,client):
        assert client.post("/workouts",json={"client_name":"John","workout_type":"Cardio","duration_min":45}).status_code==201

class TestPrograms:
    def test_get(self,client):
        assert client.get("/programs").status_code==200

class TestAuth:
    def test_login(self,client):
        assert client.post("/login",json={"username":"admin","password":"admin123"}).status_code==200
    def test_bad(self,client):
        assert client.post("/login",json={"username":"x","password":"x"}).status_code==401
