/// CONSTANTS ///
var getData_endpoint = "../getalldataset"

var dataset = [] //This is the dataset object that will be acessed by all



/// FUNCTIONS ///

//Function call to get the the data from the ../getalldataset endpoint in flask
function getAllData(){
	$.get( getData_endpoint, function( data ) {
	  console.log(data)
	  dataset = data 
	  //alert( "Load was performed." );
	});	
}



function addClient(){
	//Add a Client
}

function refreshGraph(graph_id, datapoints){
	//Refresh a graph with new datapoints
}



function setup(){
	//Setup
	//
}


//This schedules the getAllData to be ran every 5 sec.
window.setInterval(getAllData, 5000);

