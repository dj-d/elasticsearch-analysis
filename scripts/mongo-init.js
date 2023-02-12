const fs = require('fs');

const dbName = 'revision_history_db';

db = db.getSiblingDB(dbName);

db.createCollection('revision_history_collection');

fs.readdirSync('/archive').forEach(file => {
    console.log(file);
    db.revision_history_collection.insertMany(require('/archive/'+ file));
});