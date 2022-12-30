from dao.game_dao import GameDao
from dao.game_dao import PlayerDao
from dao.game_dao import VesselDao
from model.game import Game
from model.battlefield import Battlefield
from model.frigate import Frigate
from model.submarine import Submarine
from model.destroyer import Destroyer
from model.cruiser import Cruiser
from model.player import Player


class GameService:
    def __init__(self):
        self.game_dao = GameDao()
        self.player_dao=PlayerDao()
        self.vessel_dao=VesselDao()


    def create_game(self, player_name: str, min_x: int, max_x: int, min_y: int,max_y: int, min_z: int, max_z: int) -> int:
        game = Game()
        battlefield = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z)
        game.add_player(Player(player_name, battlefield))
        return self.game_dao.create_game(game)

    def join_game(self, game_id: int, player_name: str) -> bool:
        battlefield=Battlefield()
        player=Player(player_name,battlefield)
        self.player_dao.create_player(player,game_id)
        game=self.game_dao.find_game(game_id)
        return(player in game.get_players() )

    def get_game(self, game_id: int) -> Game:
        game = self.game_dao.find_game(game_id)
        return(game)


    def add_vessel(self , vessel_type: str,x: int, y: int, z: int,game_id: int, player_name: str) -> bool:
        if vessel_type=="frigate":
            vessel=Frigate(x,y,z)
        elif vessel_type=="submarine":
            vessel=Submarine(x,y,z)
        elif vessel_type=="destroyer":
            vessel=Destroyer(x,y,z)
        elif vessel_type =="cruiser":
            vessel=Cruiser(x,y,z)
        self.vessel_dao.create_vessel(vessel, player_name, game_id)
        player=self.player_dao.find_player(player_name,game_id)
        vessels=player.get_battlefield().get_vessels()
        return(vessel in vessels)


    def shoot_at(self, game_id: int, shooter_name: str, vessel_id: str, x: int,y: int, z: int) -> bool:
        vessel=self.vessel_dao.find_vessel(vessel_id,shooter_name,game_id)
        vessel.fire_at(x,y,z)
        return (vessel.get_hits()!=0)

    def get_game_status(self, game_id: int, shooter_name: str) -> str:
        game=self.game_dao.find_game(game_id)
        L=game.get_players()
        c=0
        for player in L :
            battlefield=player.get_battlefield()
            if battlefield.get_power()==0:
                c+=1
                L.remove(player)
        if c==0:
            return("EN COURS")
        elif self.game_dao.find_player(shooter_name,game_id)not in L:
            return("Perdu")
        else :
            return("GAGNE")
