#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   Javbus.py
@Time    :   2019/12/25 22:09
@Author  :   cha0sCat
@Version :   1.0
@Contact :   admin@noob.pw
@License :   (C)Copyright 2017-2019, cha0sCat
@Desc    :   None
"""
import json
from google.cloud import datastore

client = datastore.Client(project="javbus")


def count():
    query = client.query(kind="Javbus")
    query.keys_only()
    Javbus = str(len(list(query.fetch())))

    query = client.query(kind="Javbus")
    query.keys_only()
    Javbus_Stars = str(len(list(query.fetch())))
    return f"Javbus: {Javbus}\nJavbus_Stars: {Javbus_Stars}"


def main(request):
    if request.method == "POST":
        data = json.loads(request.form['data'])
        kind = "Javbus"
        name = data["code"]
        key = datastore.Key(kind, name)
        entity = datastore.Entity(key=key, exclude_from_indexes=["previews", "magnets"])
        client.put(entity)
    else:
        return count()
