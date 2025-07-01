/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2149151412")

  // add field
  collection.fields.addAt(1, new Field({
    "hidden": false,
    "id": "number3932642694",
    "max": null,
    "min": null,
    "name": "log_id",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(2, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text1843675174",
    "max": 0,
    "min": 0,
    "name": "description",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2149151412")

  // remove field
  collection.fields.removeById("number3932642694")

  // remove field
  collection.fields.removeById("text1843675174")

  return app.save(collection)
})
