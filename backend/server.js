const keys = require('./keys');
const express = require('express');
const {MongoClient} = require('mongodb');
const bodyparser = require('body-parser');
const cors = require('cors');


const PORT = process.env.port || 4000;

const express_app = express();
express_app.use(bodyparser.json());
express_app.use(cors());

var db;

express_app.listen(PORT, ()=>{
   MongoClient.connect((keys.mongoURI), {newUrlParser: true}, (error, db_obj)=>{
        console.log('Connected to MongoDB...');
        db = db_obj.db('SaveTheManuals');
    });
   console.log(`Server listening on port ${PORT}...`);
});


express_app.get('/cars', async function(req, res){

    let cars = {};
    try {
        cars = await db
                    .collection('cars')
                    .find()
                    .sort({_id: -1})
                    .limit(1)
                    .toArray();
       
    }catch(error) {
        console.log(error);
    }
    

    console.log(cars[0]);
    res.send(cars[0]);

});



