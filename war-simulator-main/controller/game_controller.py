import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model.game import Game
Game.excluded_keys = ['_sa_instance_state']
from services.game_service import GameService
app = FastAPI()
game_service = GameService()

class CreateGameData(BaseModel):
    player_name: str
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    min_z: int
    max_z: int

@app.post("/create-game")
async def create_game(player_name:str,min_x:int,max_x:int,min_y:int,max_y:int,min_z:int,max_z:int):
    return game_service.create_game(player_name, min_x,max_x, min_y,max_y, min_z,max_z)

@app.get("/get-game")
async def get_game(game_id: int) -> Game:
    return game_service.get_game(game_id)

@app.post("/join-game")
async def join_game(game_id:int,player_name:str) -> bool:
    return game_service.join_game(game_id,player_name)

@app.post("/add-vessel")
async def add_vessel(vessel_type:str,x:int,y:int,z:int,game_id:int,player_name:str) -> bool:
    return game_service.add_vessel(vessel_type,x, y, z,game_id, player_name)

@app.post("/shoot-at")
async def shoot_at(game_id:int,shooter_name:str,vessel_id:int,x:int,y:int,z:int) -> bool:
    return game_service.shoot_at(game_id
            , shooter_name, vessel_id, x, y, z)


@app.get("/game-status")
async def get_game_status(game_id: int, player_name: str) -> str:
    return game_service.get_game_status( game_id, player_name)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500,content={"message": f"{exc}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

from starlette.staticfiles import StaticFiles
app = FastAPI()
BASE_PATH = Path(__file__).resolve().parent.parent
app.mount("/views", StaticFiles(directory=BASE_PATH / 'views'), name="views")
