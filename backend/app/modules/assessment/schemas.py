from pydantic import BaseModel


class AssessmentIn(BaseModel):
    answers: dict


class AssessmentOut(BaseModel):
    id: str
    answers: dict

    class Config:
        from_attributes = True
