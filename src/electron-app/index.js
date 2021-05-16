var awsIot = require('aws-iot-device-sdk');

const topic = 'cs498/time/leetcode'
const pub_topic = 'cs498/time/new'
const clientId = 'time-' + (Math.floor((Math.random() * 100000) + 1));
// console.log(clientId)
var device = awsIot.device({
    keyPath: 'certificates/56cd19a9b5-private.pem.key',
    certPath: 'certificates/56cd19a9b5-certificate.pem.crt',
    caPath: 'certificates/AmazonRootCA1.pem',
    clientId: clientId,
    host: 'a2wcug9wfns56q-ats.iot.us-east-2.amazonaws.com',
    maximumReconnectTimeMs: 5000,
    connectTimeout: 5000,

    debug: true,
    // autoResubscribe: false
});

const loading = "Loading..."

var prob_pool = []


function getNextProb() {
    var next_prob = prob_pool.pop()
    if (!next_prob) {
        return next_prob
    }
    for (var key in next_prob) {
        if (next_prob.hasOwnProperty(key)) {
            return [key, next_prob[key]];
        }
    }

}


function getCurrentProblem() {
    let p_slug = document.getElementById("p_slug").innerHTML;
    let p_id = document.getElementById("p_id").innerHTML;
    return [p_slug, p_id]
}


function updateProblem(new_data = false) {
    let [p_slug, p_id] = getCurrentProblem();
    if (new_data && p_slug !== loading) {
        return
    }
    next_prob = getNextProb();
    new_p_slug = 'Loading...';
    new_p_id = 'Loading...';
    if (next_prob) {
        var [new_p_slug, new_p_id] = next_prob;
    }
    document.getElementById("p_slug").innerHTML = new_p_slug;
    document.getElementById("p_id").innerHTML = new_p_id;
}


function sendAck(e) {
    let [p_slug, p_id] = getCurrentProblem();

    updateProblem();
    payload = { 'ack': true, 'slug': p_slug, 'id': p_id };
    publish(JSON.stringify(payload));

}


function updateUI(data) {
    response = JSON.parse(data)
    if (!Array.isArray(prob_pool) || !prob_pool.length) {
        // console.log(prob_pool)
        console.log(response.problems)
        prob_pool = response.problems;
        updateProblem(new_data = true);
        console.log(prob_pool)
    }
    today_count = response['todayCount']
    if (today_count < 10) {
        document.getElementById("today").innerHTML = `${10 - today_count}/10 Remaining.`;
    } else {
        document.getElementById('today').innerHTML = `${today_count} problems solved so far.`;
    }

    // document.getElementById("p_slug").innerHTML = prob_pool[0];
    // document.getElementById("p_id").innerHTML = prob_pool[0];
    document.getElementById("easy").innerHTML = response['ac_easy'];
    document.getElementById("medium").innerHTML = response['ac_medium'];
    document.getElementById("hard").innerHTML = response['ac_hard'];
    // document.getElementById("temperature").innerHTML = `${response['temperature']} &#8451;`

}


function publish(message) {
    device.publish(pub_topic, message);
}

device
    .on('connect', function () {
        console.log('connect');
        device.subscribe(topic);
        document.getElementById('con-status').innerHTML = 'Connected.';
    });

device
    .on('message', function (topic, payload) {
        console.log('message', topic, payload.toString());
        updateUI(payload.toString());
    });


device
    .on('reconnect', function (topic, payload) {
        console.log('reconnect');
    });

device.on('error', (error) => {
    // error.message might be 'premature close'
    console.log(error)
});