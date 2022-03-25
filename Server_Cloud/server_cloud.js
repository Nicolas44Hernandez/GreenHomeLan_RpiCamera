const express = require('express')
const cors = require('cors');
const fs = require('fs');
const app = express()
const port = 8000
let json
const path = './boxesip.json';
const bodyParser = require('body-parser')

app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static(__dirname + '/www'));

function FileExist(){
    if (fs.existsSync(path)) {
        json = require(path);
        console.log(json)
    }
    else{
        console.log('boxesip.json not exist launch postMyIp.py form rpi_box')
    }
}

app.get('/boxes_ip/:box_name', (req, res) => {
    const name_box  = req.params[Object.keys(req.params)[0]]
    res.send(JSON.stringify(json[name_box]))
  })

app.post('/boxes_ip', (req, res) => {
    const dict = {box_name:req.body.name, rpi_box:req.body.ip};
    const dictstring = JSON.stringify(dict)
    fs.writeFile(("boxesip.json"), dictstring, () => {})
    res.status(201).json(dict)
})

app.listen(port, () => {
    console.log(`Server cloud listening on port ${port}`)
})

FileExist()