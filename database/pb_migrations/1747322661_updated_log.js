/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2149151412")

  // update collection data
  unmarshal({
    "name": "logs"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2149151412")

  // update collection data
  unmarshal({
    "name": "log"
  }, collection)

  return app.save(collection)
})
