// Update frame
function update(){
    console.log("Updating...")
    $.ajax({
        url: "get_frame",
        success: function(data){
            console.log("Got frame data : " + data.length + " bytes");
            $("#preview_cam").attr("src", "data:image/jpeg;base64,"+data);
            update();
        },
        error: function(data){
            console.log("Timeout");
            update();
        },
        timeout: 50
    });
}


$(document).ready(function(){
    console.log("Ready");
    setTimeout(update, 100);
})
