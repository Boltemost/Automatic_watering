/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1639572554")

  // add field
  collection.fields.addAt(2, new Field({
    "hidden": false,
    "id": "number392174304",
    "max": null,
    "min": null,
    "name": "humd",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1639572554")

  // remove field
  collection.fields.removeById("number392174304")

  return app.save(collection)
})
