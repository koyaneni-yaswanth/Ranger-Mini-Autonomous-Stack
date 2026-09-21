const ROSBRIDGE_PORT = 9090;
const WEBVIDEO_PORT = 8080;

// Get current hostname so it works on any network
const hostname = window.location.hostname || 'localhost';

// Setup Rosbridge Connection
const ros = new ROSLIB.Ros({
    url: `ws://${hostname}:${ROSBRIDGE_PORT}`
});

ros.on('connection', function() {
    console.log('Connected to websocket server.');
    document.getElementById('status-indicator').className = 'w-4 h-4 rounded-full bg-green-500';
    document.getElementById('status-text').innerText = 'Connected to ROS 2';
    
    // Set video stream source
    document.getElementById('camera-feed').src = `http://${hostname}:${WEBVIDEO_PORT}/stream?topic=/camera/image&type=ros_compressed`;
});

ros.on('error', function(error) {
    console.log('Error connecting to websocket server: ', error);
    document.getElementById('status-indicator').className = 'w-4 h-4 rounded-full bg-yellow-500';
    document.getElementById('status-text').innerText = 'Error connecting to ROS 2';
});

ros.on('close', function() {
    console.log('Connection to websocket server closed.');
    document.getElementById('status-indicator').className = 'w-4 h-4 rounded-full bg-red-500';
    document.getElementById('status-text').innerText = 'Disconnected from ROS 2';
});

// Odometry Subscriber
const odomSub = new ROSLIB.Topic({
    ros: ros,
    name: '/odom',
    messageType: 'nav_msgs/msg/Odometry'
});

odomSub.subscribe(function(message) {
    document.getElementById('odom-x').innerText = message.pose.pose.position.x.toFixed(2);
    document.getElementById('odom-y').innerText = message.pose.pose.position.y.toFixed(2);
});

// Velocity Publisher (for E-Stop)
const cmdVelPub = new ROSLIB.Topic({
    ros: ros,
    name: '/cmd_vel',
    messageType: 'geometry_msgs/msg/Twist'
});

function stopRobot() {
    console.log("EMERGENCY STOP");
    const twist = new ROSLIB.Message({
        linear: { x: 0, y: 0, z: 0 },
        angular: { x: 0, y: 0, z: 0 }
    });
    cmdVelPub.publish(twist);
}

// Mission Trigger
function startPatrol() {
    console.log("Triggering Patrol Mission (Requires mission node to be running)");
    alert("Patrol Mission Triggered! (Ensure patrol_mission is running)");
    // In a full implementation, you would call a ROS 2 Action or Service here
}
