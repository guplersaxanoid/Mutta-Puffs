new QWebChannel(qt.webChannelTransport,function(channel){
    window.backend = channel.objects.backend;
});
markers = null;
loc = null
teams = []
var map = L.map('map').setView([51.505, -0.09], 13);
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoiZ3VwbGVyc2F4YW5vaWQiLCJhIjoiY2tuN2tqcXN2MGowcDJwbnpwcTRnZ3B1dyJ9.AQghSlPVVlTuLdk3b2kI0A'
}).addTo(map);
function addMarkers(e){
    if(markers!=null)
        map.removeLayer(markers);
    loc = e.latlng;
    markers = L.marker(e.latlng,{draggable:true});
    map.addLayer(markers);
    document.getElementById("stadium-location").innerHTML="( "+e.latlng.lat+", "+e.latlng.lng+" )";
}
const provider = new window.GeoSearch.OpenStreetMapProvider();
const search = new GeoSearch.GeoSearchControl({
    provider: provider,
    style: 'bar',
    updateMap: true,
    showMarker: false
}).addTo(map);
map.on('click',addMarkers);

function addTeam(){
    if(!validateTeam()) return;
    document.getElementById("validation-message").innerHTML = "";
    var name = document.forms["team-info-input"]["team-name"].value;
    var abbr = document.forms["team-info-input"]["abbr"].value;
    var location = loc.lat+","+loc.lng
    teams.push({"name":String(name), "abbr":String(abbr), "location":location});
    e = document.createElement("div");
    e.setAttribute("id",String(abbr));
    p1 = document.createElement("p");
    p1.innerHTML=String(teams.length)+". "+String(name)+" ("+String(abbr)+")"+" at "+"( "+location+")";
    p1.setAttribute("class","team-list-item");
    e.appendChild(p1);
    document.getElementById("team-list").appendChild(e);
    document.forms["team-info-input"].reset();
    document.getElementById("stadium-location").innerHTML="";
    map.removeLayer(markers);
    return true;
}



function validateTeam(){
    var name = document.forms["team-info-input"]["team-name"].value;
    if(name==""){
        document.getElementById("validation-message").innerHTML = "Please enter a team name";
        return false;
    }
    var abbr = document.forms["team-info-input"]["abbr"].value;
    if(abbr==""){
        document.getElementById("validation-message").innerHTML = "Please enter a 3 letter abbreviation for the team name";
        return false;
    }
    if(markers==null){
        document.getElementById("validation-message").innerHTML = "Please mark the location of home stadium in the map";
        return false;
    } else {
        document.getElementById("validation-message").innerHTML = "";
        return true;
    }
}

function removeTeam(){
    var abbr = teams[teams.length-1]["abbr"];
    teams.splice(teams.length-1,1);
    var c = document.getElementById(abbr);
    c.parentNode.removeChild(c);
}

function writeInputs(){
    if(teams.length<4){
        alert("Please add atleast 4 teams");
        return false;
    } 
    if(teams.length%2==1){
        alert("Round-robin tournament requires even number of teams. Please add or remove a team");
        return false;
    }
    backend.getInput(JSON.stringify(teams));
    backend.goToNextPage();
}