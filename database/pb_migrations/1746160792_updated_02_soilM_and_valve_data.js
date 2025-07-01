/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1670799962")

  // add field
  collection.fields.addAt(3, new Field({
    "hidden": false,
    "id": "bool3535425587",
    "name": "valve_state",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "bool"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1670799962")

  // remove field
  collection.fields.removeById("bool3535425587")

  return app.save(collection)
})
