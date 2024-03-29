from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

from .objectid import PydanticObjectId

def parse_json(data):
    # TODO - Encriptar id
    return json.loads(json_util.dumps(data))

class Category(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    image_url: Optional[str]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class Trip(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    description: str
    categories: List[str]
    image_url: Optional[str]
    # categories: List[Category]
    dropoff_location: str

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class Operator(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    type: str
    name: str
    description: Optional[str]
    social_networks: object
    logo_url: Optional[str]
    inactive: Optional[bool]
    pickup_city_ids: List[str]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class Itinerary(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    pickup_city_ids: List[str]
    price: Optional[Union[int, float]]
    date: datetime
    description: Optional[str]
    classification: str
    trip_id: str
    operator_id: str

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class Tagged(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    already_know: bool
    user_id: str
    trip_id: Optional[str]
    itinerary_id: Optional[str]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    email: str
    name: str
    city_id: Optional[str]
    google_id: str

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class City(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    uf: str

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
