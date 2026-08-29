console.log("FitLog is connected"); 

fetch("http://localhost:8000/api/test")
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });