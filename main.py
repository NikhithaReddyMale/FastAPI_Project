import json
from typing import Annotated, Literal, Optional

from fastapi import (  # pyright: ignore[reportMissingImports]
    FastAPI,
    HTTPException,
    Path,
    Query,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Id of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[
        Optional[str],
        Field(default="Hyderabad", description="Patient is from which city"),
    ]
    age: Annotated[int, Field(..., description="Age of the patient")]
    gender: Annotated[
        Literal["Male", "Female", "Others"],
        Field(..., description="Gender of the patient"),
    ]
    height: Annotated[float, Field(..., description="Height in mtrs")]
    weight: Annotated[float, Field(..., description="Weight in kgs")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / self.height * self.height, 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


app = FastAPI()


def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
        return data


def write_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {"message": "A fully functional API to manage your patient records"}


@app.get("/view")
def view_data():
    data = load_data()
    return data


@app.get("/view/{patient_id}")
def view_patient(
    patient_id: str = Path(
        ..., description="ID of the patient in the DB", example="P001"
    ),
):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient id not found")


@app.get("/sort")
def sort(
    sort_by: str = Query(..., description="Sort by height , weight or bmi only"),
    order: str = Query("asc", description="Sort in asc or desc"),
):
    valid_fields = ["age", "height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid field , select from {valid_fields}"
        )
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Bad Request Invalid request select from asc and desc",
        )

    data = load_data()
    reverse_order = order == "desc"
    sorted_data = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=reverse_order
    )
    return sorted_data


@app.post("/create")
def create_patient(patient: Patient):

    # get existing patients data
    existing_patients = load_data()

    # verify if current patient is not in existing
    if patient.id in existing_patients:
        raise HTTPException(status_code=400, detail=f"{patient.id} already exists")

    json_patient_data = patient.model_dump(exclude="id")
    existing_patients[patient.id] = json_patient_data

    # write back this
    write_data(existing_patients)
    return JSONResponse(
        status_code=201, content={"message": "Patient record created successfully"}
    )
