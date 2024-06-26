from fastapi import FastAPI, Body, Path, Query, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Coroutine, Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

app = FastAPI() # uvicorn main:app --reload 
app.title = "Prueba de FastAPI"
app.version = "0.0.1"

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):        
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data["email"] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales invalidas")        

class User(BaseModel):
    email:str
    password:str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5 ,max_length=15)
    overview: str = Field(max_length=25)
    year: int = Field(le=2025)
    rating: float = Field(ge=0, le=10)
    category: str
    
    class Config:
        json_schema_extra = {            
            "example":{
                "id":1,
                "title":"Mi pelicula",
                "overview":"Descripcion Pelicula",
                "year":2022,
                "rating":9.5,
                "category":"Accion"
            }
        }
movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que...",
        "year": "2009",
        "rating": 7.8,
        "category": "Acción"
    },
    {
        "id": 2,
        "title": "Dune",
        "overview": "Pelicula en el desierto....",
        "year": "2019",
        "rating": 8.8,
        "category": "Acción"
    }
]



@app.get('/', tags=["home"])
def message():
    return HTMLResponse("<h1>Aguante San Lorenzo!</h1>")

@app.get("/login", tags=["auth"])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content=token)    

@app.get("/movies", tags=["movies"], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)

@app.get("/movies/{id}", tags=["movies"], response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
    for item in movies:
        if item["id"] == id:
            return JSONResponse(content=item)
                
    return JSONResponse(status_code=404, content=[])

@app.get("/movies/", tags=["movies"],response_model=List[Movie]) # con la barra al final 
def get_movies_by_categories(category: str = Query(min_length=5, max_length=25)) -> List[Movie] :
    data = [ item for item in movies if item['category'] == category ]
    return JSONResponse(content=data)


@app.post("/movies", tags=["movies"], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    movies.append(movie.model_dump())
    return JSONResponse(status_code=201, content={"message": "Se ha registrado la pelicula"})

@app.put("/movies/{id}", tags=["movies"], response_model=dict, status_code=200)
def edit_movie(id: int, movie: Movie) -> dict:
    for item in movies:
        if item["id"]== id:
            item["title"]=movie.title
            item["overview"]=movie.overview
            item["year"]=movie.year
            item["year"]=movie.year
            item["rating"]=movie.rating
            item["category"]=movie.category
            return JSONResponse(status_code=200, content={"message":"Se ha modificado la pelicula"})
        
@app.delete("/movies/{id}", tags=["movies"], response_model=dict, status_code=200)
def delete_movie(id:int) -> dict:
    for item in movies:
        if item["id"] == id:
            movies.remove(item)
            return JSONResponse(status_code=200, content={"message": "Se ha eliminado la pelicula"})