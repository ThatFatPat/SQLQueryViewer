const express = require('express')
const app = express()
const port = 3000
const settings = require('./settings.json')
const sql = require("mssql")
const fs = require("fs")
fs.readFile("./settings.json", "utf8", (err, jsonString) => {
    if (err) {
        console.log("File read failed:", err)
        return
    }
    console.log("File data:", jsonString)
    try {
        global.settings = JSON.parse(jsonString)
        console.log(global.settings.databases)
    } catch(err) {
        console.log('Error parsing JSON string:', err)
        return
    }
})

app.get('/', (req, res) =>{
    // config for your database
    for(database of global.settings.databases){
        sql.connect(database, function (err){
            console.log("Connceted!")
            // create Request object
            var request = new sql.Request(pool);
               
            // query to the database and get the records
            request.query('select * from sys.objects', function (err, recordset) {

                if (err) console.log(err)
    
                // send records as a response
                res.send(recordset);
                
            });
        });
        sql.close();
    }
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
