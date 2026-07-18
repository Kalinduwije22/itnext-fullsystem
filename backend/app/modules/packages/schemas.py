from pydantic import BaseModel


class PackageOut(BaseModel):
    id: str
    slug: str
    name: str
    price_lkr: float
    description: str

    class Config:
        from_attributes = True
