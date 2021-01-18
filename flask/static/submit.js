function submitScore(event){
    event.preventDefault();
    var score = 0;
    for(var i = 0; i<14; i++){
        if(document.getElementById("Activity"+i).checked){
            score = Math.max(score, document.getElementById("Activity"+i).value);
        }
    }
    console.log(score);
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){ }
    };
    xhttp.open("POST", "http://localhost:5000/sendScore", true);
    var data = new FormData();
    data.append('score', score);
    xhttp.send(data);
}
