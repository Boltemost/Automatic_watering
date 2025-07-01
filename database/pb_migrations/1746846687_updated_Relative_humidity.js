/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3503515176")

  // update collection data
  unmarshal({
    "name": "relative_humidity"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3503515176")

  // update collection data
  unmarshal({
    "name": "Relative_humidity"
  }, collection)

  return app.save(collection)
})
