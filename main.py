import json

from fastapi import (  # pyright: ignore[reportMissingImports]
    FastAPI,
    HTTPException,
    Path,
    Query,
)

app = FastAPI()


def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
        return data


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
        raise HTTPException(status_code=400, detail=f"Invalid field , select from {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Bad Request Invalid request select from asc and desc")

    data = load_data()
    reverse_order = order == "desc"
    sorted_data = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=reverse_order
    )
    return sorted_data
