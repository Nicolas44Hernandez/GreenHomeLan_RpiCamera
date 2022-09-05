const bodyParser = require('body-parser');
const express = require('express');
const exec = require('child_process').exec;
const Gpio = require('onoff').Gpio;

const app = express();
const port = 4000;
const button = new Gpio(6, 'in', 'rising', {debounceTimeout: 20});
const web = new Gpio(26, 'in', 'rising', {debounceTimeout: 20});
const wifi_pin = new Gpio(14, 'out');
let last_frame;

app.listen(port, () => { 
    console.log(`-----------------------------------------> Server Camera listening on port ${port}`)
}); 

app.use(express.static(__dirname + '/www'));
app.use(bodyParser.urlencoded({
    limit: '200mb',
    extended: true
}))

button.watch((err, value) => {
    console.log('appui sur bouton BLE pour activer le wifi du rpicam');
    setWifiOn('button');
}); 

process.on('SIGINT', _ => {
    button.unexport();
});

web.watch((err, value) => {
    console.log('appui sur web BLE pour activer le wifi du rpibox')
    setWifiOn('web');
}); 

process.on('SIGINT', _ => {
    web.unexport();
});

function initServer(){
    console.log('Init Server');
    setWifiOff();
}

async function setWifiOn(type_command){
    let command = `sudo service hostapd start`;
    wifi_pin.writeSync(1);
    exec(command);
    if (type_command == "button"){
        console.log("wifi on by button");
    }
    if (type_command == "web"){
        console.log("wifi on by web");
    }
    command = `python3 captureVideo.py`;
    exec(command);
    console.log("captureVideo Launched!");
}

async function setWifiOff(){
    let command = `sudo service hostapd stop`;
    console.log("       Command to stop Wi-Fi");
    wifi_pin.writeSync(0);
    exec(command);
    console.log("       LED Wi-Fi is off");
    console.log("       Wi-FI is off");
    command = `kill $(ps aux | grep '[p]ython3 captureVideo.py' | awk '{print $2}')`;
    exec(command);
    console.log("       kill process captureVideo.py");  
}

function getFrame(res) {
    if (last_frame != undefined) {
        res.end(last_frame);
        last_frame = undefined;
    }
}

function frameData(req, res) {
    last_frame = req.body.data;
    res.end();
}

app.post("/frame_data", (req, res) => {
    frameData(req, res);
});

app.get("/get_frame", (req, res) => {
    console.log("get_frame");
    getFrame(res);
});

app.get("/closewifi", (req, res) => {
    console.log("---> Receive GET /closewifi from box to shutdown wifi");
    setWifiOff();
    res.send('Wi-Fi of camera is off');
    console.log("<--- Send response GET /closewifi to box : Wi-FI is off");
});

initServer();