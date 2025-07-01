/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2367391513")

  // update collection data
  unmarshal({
    "name": "presets"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2367391513")

  // update collection data
  unmarshal({
    "name": "Presets"
  }, collection)

  return app.save(collection)
})
