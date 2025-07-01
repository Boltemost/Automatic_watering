/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1639572554")

  // update collection data
  unmarshal({
    "name": "temperature"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1639572554")

  // update collection data
  unmarshal({
    "name": "Temperature"
  }, collection)

  return app.save(collection)
})
