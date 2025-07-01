/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3275585383")

  // add field
  collection.fields.addAt(1, new Field({
    "hidden": false,
    "id": "number2194901947",
    "max": null,
    "min": null,
    "name": "water_flow_lph",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(2, new Field({
    "hidden": false,
    "id": "number2947769879",
    "max": null,
    "min": null,
    "name": "water_tank_level",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(3, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text1175934358",
    "max": 0,
    "min": 0,
    "name": "Inlet",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3275585383")

  // remove field
  collection.fields.removeById("number2194901947")

  // remove field
  collection.fields.removeById("number2947769879")

  // remove field
  collection.fields.removeById("text1175934358")

  return app.save(collection)
})
