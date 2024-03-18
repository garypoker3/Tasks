from django.db import models
import pandas as pd


class DataFrameModel(models.Model):
    data = models.JSONField()

    @classmethod
    def load_dataframe(cls):
        """Converts model jsonField to the DataFrame and returns it."""
        obj = cls.objects.first()
        if obj:
            return pd.read_json(obj.data)
        else:
            return None  # Handle the case where there's no data stored
