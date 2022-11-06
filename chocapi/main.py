"""API implementation of CHOC functionality."""
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import scipy.optimize

# /v1/choc/models/cho
# /v1/choc/models/fat
# {
#  "watts": [0, 75, 100, 125, 150, 175, 200, 225, 275],
#  "consumption": [21, 38, 50, 63, 83, 104, 121, 142, 250]
#}
# {
# "watts": [0, 125, 150, 175, 200, 225, 250, 275],
# "consumption": [13, 31, 31, 33, 29, 25, 17, 0]
#}


class ModelName(str, Enum):
    """Class representing the different model types."""
    cho = "cho"
    fat = "fat"

# create the API object
app = FastAPI()

class Data(BaseModel):
    """Class representing the data to be used for the model."""
    watts: list[int] =[]
    consumption: list[int] = []

class Model(BaseModel):
    """Class representing the model."""
    model: ModelName
    param_1: float
    param_2: float
    param_3: float
    fit_quality: float


def mono_exp(x_value, m_value, t_value, b_value):
    """Monotonic exponential function reflecting the carbohydrates consumption."""
    # CHO consumption is 0 beyond that wattage
    #if x >= 275:
    #    return 0
    return m_value * np.exp(-t_value * x_value) + b_value

def square_exp(x_value, a_value, b_value, c_value):
    """Square exponential function reflecting the fat consumption."""
    # CHO consumption is 0 beyond that wattage
    #if x >= 275:
    #    return 0
    return a_value * np.square(x_value) + b_value * x_value + c_value

def fit_quality(func, yarray):
    """Calculate the fit quality of the model."""
    sq_diffs = np.square(yarray - func)
    sq_diffsfrommean = np.square(yarray - np.mean(yarray))
    r_sq = 1 - np.sum(sq_diffs) / np.sum(sq_diffsfrommean)
    return r_sq


@app.post("/models/{model_name}", response_model=Model)
async def create_model(model_name: ModelName, data: Data):
    """Create a model(CHO or FAT)."""

    # Create numpy arrays from the data
    watt_values = np.array(data.watts)
    consumption_values = np.array(data.consumption)

    # number of elements in the arrays must be greater than 3
    if len(watt_values) < 3 or len(consumption_values) < 3:
        raise HTTPException(status_code=422,
            detail="Not enough data, at least 3 data points required")

     # check for identical number of elements in the arrays
    if len(watt_values) != len(consumption_values):
        # raise http exception
        raise HTTPException(status_code=422,
            detail="Number of elements in the arrays are not equal")

    # check for values in the arrays that are negative
    if np.any(watt_values < 0) or np.any(consumption_values < 0):
        # raise http exception
        raise HTTPException(status_code=422,
            detail="Negative values not allowed")

    if model_name is ModelName.cho:
        # Fit the data to the monoExp function
        initial_guess = (1, -0.1, 1)
        # pylint: disable=unused-variable
        optimal_values, covariance, *remaining_params = scipy.optimize.curve_fit(mono_exp,
                            watt_values, consumption_values, initial_guess)
        m_value, t_value, b_value = optimal_values

        # Quality of the CHO curve fit
        r_square = fit_quality(mono_exp(watt_values,m_value,t_value,b_value), consumption_values)

        # Create the return model
        cho_model = Model(model=model_name, param_1=m_value,
                            param_2=t_value, param_3=b_value, fit_quality=r_square)

        return cho_model

    if model_name is ModelName.fat:
        # Fit the data to the of the suqare root function
        fit = np.polyfit(watt_values, consumption_values, 2)
        a_value, d_value, c_value = fit

        # Quality of the FAT curve fit
        r_square = fit_quality(square_exp(watt_values,a_value,d_value,c_value), consumption_values)

        # Create the return model
        fat_model = Model(model=model_name, param_1=a_value,
                            param_2=d_value, param_3=c_value, fit_quality=r_square)

        return fat_model

    return {"model_name": model_name, "message": "Have some residuals"}
