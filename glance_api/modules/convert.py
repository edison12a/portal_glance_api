import json
from sqlalchemy.inspection import inspect
import sqlalchemy.orm

from datetime import date, datetime


def jsonify(query):
    result = []

    for row in query:
        to_append = {}

        # get object columns and data
        for column in row.__table__.columns:
            column_header = str(column).split('.')[1]
            to_append[column_header] = getattr(row, column_header)

        # get objects relationship columns and data
        inspect_row = inspect(row).__dict__['class_'].__dict__.keys()

        for column_name in inspect_row:
            if not column_name.startswith('_'):
                if column_name not in row.__table__.columns:
                    if '_sa_adapter' in getattr(row, column_name).__dict__.keys():
                        # 'sqlalchemy.orm.collections.InstrumentedList'
                        item_collect = []

                        for relationship_row in getattr(row, column_name):
                            item = {}
                            for data in relationship_row.__table__.columns:
                                item[str(data).split('.')[1]] = getattr(relationship_row, str(data).split('.')[1])

                            item_collect.append(item)

                        to_append[column_name] = item_collect

                    else:
                        # 'sqlalchemy.orm.dynamic.AppenderBaseQuery'
                        item_collect = []

                        for relationship_row in getattr(row, column_name):
                            item = {}
                            for data in relationship_row.__table__.columns:
                                item[str(data).split('.')[1]] = getattr(relationship_row, str(data).split('.')[1])

                            item_collect.append(item)

                        to_append[column_name] = item_collect

        result.append(to_append)

    return result
