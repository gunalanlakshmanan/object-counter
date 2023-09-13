from typing import List

from pymongo import MongoClient
from sqlalchemy import create_engine, Table, select, insert, update
from sqlalchemy.ext.declarative import declarative_base

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountSQLRepo(ObjectCountRepo):

    def __init__(self, user, pswd, host, port, database):
        self.db_engine = create_engine(f"postgresql://{user}:{pswd}@{host}:{port}/{database}")
        base = declarative_base()
        self.ObjectCounter = Table(
            'object_counter', base.metadata, autoload_with=self.db_engine, schema='object_detection'
        )

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        object_counts = []
        with self.db_engine.connect() as conn:
            query = select(self.ObjectCounter)
            result_set = conn.execute(query)
            if result_set.rowcount:
                result_set = result_set.all()
                for row in result_set:
                    object_counts.append(ObjectCount(row.object_class, row.count))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        with self.db_engine.connect() as conn:
            for value in new_values:
                query = select(self.ObjectCounter).where(self.ObjectCounter.c.object_class == value.object_class)
                result = conn.execute(query)
                if result.rowcount:
                    query = update(self.ObjectCounter)\
                        .where(self.ObjectCounter.c.object_class == value.object_class)\
                        .values(count=self.ObjectCounter.c.count+1)
                    conn.execute(query)
                else:
                    query = insert(self.ObjectCounter).values(object_class=value.object_class)
                    conn.execute(query)
            conn.commit()

