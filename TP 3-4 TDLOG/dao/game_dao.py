import random
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from model.game import Game
from model.vessel import Vessel
from model.weapon import Weapon
from model.player import Player
from model.battlefield import Battlefield
from sqlalchemy.orm import declarative_base, relationship
engine = create_engine('sqlite:///tdl.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class GameEntity(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship("PlayerEntity", back_populates="game",cascade="all, delete-orphan")

class PlayerEntity(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("GameEntity", back_populates="players")
    battlefields = relationship("BattlefieldEntity",back_populates="player", uselist=False, cascade="all, delete-orphan")

class BattlefieldEntity(Base):
    __tablename__='battlefield'
    id=Column(Integer,primary_key=True)
    min_x=Column(Integer,nullable=True)
    min_y = Column(Integer, nullable=True)
    min_z = Column(Integer, nullable=True)
    max_x = Column(Integer, nullable=True)
    max_x = Column(Integer, nullable=True)
    max_x = Column(Integer, nullable=True)
    max_power = Column(Integer, nullable=True)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("PlayerEntity", back_populates="battlefields")
    vessels= relationship("VesselEntity", back_populates="battlefield", uselist=False,
                                cascade="all, delete-orphan")

class VesselEntity(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True)
    coord_x = Column(Integer, nullable=True)
    coord_y = Column(Integer, nullable=True)
    coord_z = Column(Integer, nullable=True)
    hits_to_be_destroyed = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    battlefield_id = Column(Integer, ForeignKey("battlefield.id"), nullable=False)
    battlefield = relationship("BattlefieldEntity", back_populates="vessels")
    weapons= relationship("WeaponEntity", back_populates="vessel", uselist=False,
                          cascade="all, delete-orphan")

class WeaponEntity(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    ammunitions = Column(Integer, nullable=True)
    range= Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=False)
    vessel = relationship("VesselEntity", back_populates="weapons")

def map_to_battlefield_entity(battlefield: Battlefield) -> BattlefieldEntity:
    battlefield_entity = BattlefieldEntity()
    battlefield_entity.id = random.randint(0,100000)
    battlefield_entity.max_x = battlefield.max_x
    battlefield_entity.max_y = battlefield.max_y
    battlefield_entity.max_z = battlefield.max_z
    battlefield_entity.min_x = battlefield.min_x
    battlefield_entity.min_y = battlefield.min_y
    battlefield_entity.min_z = battlefield.min_z
    battlefield_entity.max_power = battlefield.max_power
    return battlefield_entity


def map_to_player_entity(player: Player) -> PlayerEntity:
    player_entity = PlayerEntity()
    player_entity.id=random.randint(0,100000)
    player_entity.name = player.name
    player_entity.battlefield = map_to_battlefield_entity(player.get_battlefield())
    return player_entity

def map_to_vessel_entity(battlefield_id: int, vessel: Vessel) -> VesselEntity:
    vessel_entity = VesselEntity()
    weapon_entity = WeaponEntity()
    weapon_entity.id = random.randint(0,100000)
    weapon_entity.ammunitions = vessel.weapon.ammunitions
    weapon_entity.range = vessel.weapon.range
    weapon_entity.type = type(vessel.weapon).__name__
    vessel_entity.id = random.randint(0,100000)
    vessel_entity.weapon = weapon_entity
    vessel_entity.type = type(vessel).__name__
    vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
    vessel_entity.coord_x = vessel.coordinates[0]
    vessel_entity.coord_y = vessel.coordinates[1]
    vessel_entity.coord_z = vessel.coordinates[2]
    vessel_entity.battlefield_id = battlefield_id
    return vessel_entity

def map_to_vessel_entities(battlefield_id: int, vessels: list[Vessel]) -> list[VesselEntity]:
    vessel_entities: list[VesselEntity] = []
    for vessel in vessels:
        vessel_entity = map_to_vessel_entity(battlefield_id, vessel)
        vessel_entities.append(vessel_entity)
    return vessel_entities

def map_to_game_entity(game: Game) -> GameEntity:
    game_entity = GameEntity()
    if game.get_id() is not None:
        game_entity.id = game.get_id()
    for player in game.get_players():
        pl:list[PlayerEntity]=[]
        player_entity = map_to_player_entity(player)
        pl.append(player_entity)
    game_entity.players=pl
    return game_entity

def map_to_battlefield(battlefield_entity: BattlefieldEntity) -> Battlefield:
    battlefield = Battlefield()
    battlefield.max_x = battlefield_entity.max_x
    battlefield.max_y = battlefield_entity.max_y
    battlefield.max_z = battlefield_entity.max_z
    battlefield.min_x = battlefield_entity.min_x
    battlefield.min_y = battlefield_entity.min_y
    battlefield.min_z = battlefield_entity.min_z
    battlefield.max_power = battlefield_entity.max_power
    return battlefield

def map_to_player(player_entity: PlayerEntity) -> Player:
    player = Player()
    player.name = player_entity.name
    player.battlefield = map_to_battlefield(player_entity.battlefield)
    return player_entity


def map_to_vessel(battlefield_entity_id: int, vessel_entity: VesselEntity) -> Vessel:
    vessel = Vessel()
    weapon = Weapon()
    weapon.ammunitions = vessel_entity.weapon.ammunitions
    weapon.range = vessel_entity.weapon.range
    weapon.type = type(vessel_entity.weapon).__name__
    vessel.weapon_entity = weapon
    vessel.type = type(vessel_entity).__name__
    vessel.hits_to_be_destroyed = vessel_entity.hits_to_be_destroyed
    vessel.coordinates[0] = vessel_entity.coord_x
    vessel.coordinates[1] = vessel_entity.coord_y
    vessel.coordinates[2] = vessel_entity.coord_z
    vessel.battlefield.id = battlefield_entity_id
    return vessel

def map_to_vessels(battlefield_entity_id: int, vessel_entities: list[VesselEntity]) -> list[Vessel]:
    vessels: list[Vessel] = []
    for vessel_entity in vessel_entities:
        vessel = map_to_vessel(battlefield_entity_id, vessel_entity)
        vessels.append(vessel)
    return vessels

def map_to_game(game_entity:GameEntity)-> Game:
    game=Game()
    if game_entity.id is not None:
        game.id = game_entity.id
    for player_entity in game_entity.players:
        player = Player()
        player.name = player_entity.name
        battlefield= map_to_battlefield (player_entity.battlefield)
        vessels = map_to_vessels(player_entity.battlefield.id, player_entity.battlefield.vessels)
        battlefield.vessel_entities = vessels
        player.battlefield_entity = battlefield
        game.players.append(player)
    return game_entity

class GameDao:
    def __init__(self):
        self.db_session = Session()
        Base.metadata.create_all(engine)

    def create_game(self, game: Game) -> int:
        game_entity = map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id

    def find_game(self, game_id: int) -> Game:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.execute(stmt).one()
        return map_to_game(game_entity)

class PlayerDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()
    def create_player(self, player :Player,game_id:int) -> int:
        gamee=GameDao()
        game=gamee.find_game(game_id)
        game_entity=map_to_game_entity(game)
        self.db_session.game_entity.add(map_to_player_entity(player))
        self.db_session.commit()
        return map_to_player_entity(player).id

    def find_player(self, player_name: str,game_id:int) -> Player:
        stmt = select(PlayerEntity).where(PlayerEntity.name == player_name)
        gamee=GameDao()
        game = gamee.find_game(game_id)
        game_entity = map_to_game_entity(game)
        player_entity = self.db_session.game_entity.scalars(stmt).one()
        return map_to_player(player_entity)

class VesselDao:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.db_session = Session()

    def create_vessel(self, vessel: Vessel,player_name:str,game_id:int) -> int:
        playere=PlayerDao()
        player = playere.find_player(player_name,game_id)
        player_entity = map_to_player_entity(player)
        vessel_entity = map_to_vessel_entity(vessel)
        self.db_session.player_entity.add(vessel_entity)
        self.db_session.commit()
        return vessel_entity.id

    def find_vessel(self, vessel_id: int,player_name:str,game_id:int) -> Vessel:
        stmt = select(VesselEntity).where(VesselEntity.id == vessel_id)
        playere=PlayerDao()
        player = playere.find_player(player_name, game_id)
        player_entity = map_to_player_entity(player)
        vessel_entity = self.db_session.player_entity.scalars(stmt).one()
        return map_to_vessel(vessel_entity)





