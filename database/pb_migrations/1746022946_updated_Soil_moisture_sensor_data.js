/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2111017243")

  // add field
  collection.fields.addAt(2, new Field({
    "hidden": false,
    "id": "number4055235223",
    "max": null,
    "min": null,
    "name": "soilM_sensor_2",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(3, new Field({
    "hidden": false,
    "id": "number2259864065",
    "max": null,
    "min": null,
    "name": "soilM_sensor_3",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(4, new Field({
    "hidden": false,
    "id": "number416702370",
    "max": null,
    "min": null,
    "name": "soilM_sensor_4",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(5, new Field({
    "hidden": false,
    "id": "number1875996468",
    "max": null,
    "min": null,
    "name": "soilM_sensor_5",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(6, new Field({
    "hidden": false,
    "id": "number4141366926",
    "max": null,
    "min": null,
    "name": "soilM_sensor_6",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(7, new Field({
    "hidden": false,
    "id": "number2178879000",
    "max": null,
    "min": null,
    "name": "soilM_sensor_7",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(8, new Field({
    "hidden": false,
    "id": "number291509129",
    "max": null,
    "min": null,
    "name": "soilM_sensor_8",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2111017243")

  // remove field
  collection.fields.removeById("number4055235223")

  // remove field
  collection.fields.removeById("number2259864065")

  // remove field
  collection.fields.removeById("number416702370")

  // remove field
  collection.fields.removeById("number1875996468")

  // remove field
  collection.fields.removeById("number4141366926")

  // remove field
  collection.fields.removeById("number2178879000")

  // remove field
  collection.fields.removeById("number291509129")

  return app.save(collection)
})
