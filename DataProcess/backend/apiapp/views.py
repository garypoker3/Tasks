from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import pandas as pd
from . import infer_data_types as idt
from . import misc as msc
from .models import DataFrameModel


@api_view(["POST"])
def process_file(request):
    """
    Process the uploaded file into a Pandas DataFrame
    Tries to infer columns type and convert data
    Defines data columns
    Returns data and columns definintion in Response
    Persists DataFrame into DataFrameModel
    """
    if request.method == "POST":
        file_obj = request.FILES.get("file")

        # Check if a file was uploaded
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=404)

        # use to simulate longer processing
        # time.sleep(2)

        # assuming if file is binary it's Excel and read it first, if not read CSV
        if msc.is_binary(file_obj):
            try:
                df = pd.read_excel(file_obj)
            except Exception as e:
                return Response(
                    {"error": f"Failed to read Excel format: {str(e)}"}, status=422
                )
        else:
            try:
                df = pd.read_csv(file_obj)
            except Exception as e:
                return Response(
                    {"error": f"Failed to read CSV format: {str(e)}"}, status=422
                )

        if df.empty:
            return Response(
                {"error": "No Excel or CSV data"}, status=422
            )  # 204 no-content no thrown exception

        # Persists DataFrame to db to use for explicit conversion.
        # one record only
        persist_to_model(df.to_json())

        return Response(convert_and_return_data(df))


@api_view(["POST"])
def apply_conversion(request):

    if request.method == "POST":
        try:
            df = DataFrameModel.load_dataframe()
        except Exception as e:
            return Response(
                {"error": f"Failed to read DataFrame from db: {str(e)}"}, status=422
            )
        col_def = request.data
        # apply conversion with explicitly defined column types and return response
        return Response(convert_and_return_data(df, col_def))


def persist_to_model(json_data):
    # save json to db. For testing purpose and simplicity it is only the one first record
    model = DataFrameModel.objects.first()
    if not model:
        model = DataFrameModel(data=json_data)  # create new
    else:
        model.data = json_data
    model.save()


def convert_and_return_data(df, col_def=[]):
    # apply conversion
    df = idt.infer_and_convert_data_types(df, col_def)

    # Convert DataFrame to JSON
    df_json = df.to_json(orient="records", date_format="iso")

    # Generate columns definition
    columns_def = [
        {
            "field": col,
            "df_type": str(dt),
            "width": max(df[col].astype(str).str.len()),
        }
        for col, dt in df.dtypes.items()
    ]

    return {"columns_def": columns_def, "data": df_json}
