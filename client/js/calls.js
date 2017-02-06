/// CONSTANTS ///
var getData_endpoint = "../getalldataset"
var dataset = [] //This is the dataset object that will be acessed by all

/// FUNCTIONS ///

//Function call to get the the data from the ../getalldataset endpoint in flask
function getAllData(){
	$.get( getData_endpoint, function( data ) {
	  console.log(data);

	  if ((dataset.clients == undefined) || (data.clients.length > dataset.clients.length)){
	  	n = 0
	  	if (dataset.clients != undefined){ n = dataset.clients.length}

	  	for (i = n; i < data.clients.length; i++){
			addClient(data.clients[i])
			console.log("Created: "+data.clients[i].mac)	
	  	}

	  }
		// if ((data.clients.length > dataset.clients.length) || (dataset.clients == undefined)){
		// 	//I'm assuming clients never re-organize on the list
		// 	for (i = dataset.clients.length; i < data.clients.length){
		// 		addClient(dataset.clients[i])
		// 		console.log("Created: "+dataset.clients[i].mac)
		// 	}
		// }

	  dataset = data 
	  //alert( "Load was performed." );
		  
	});	
}



function addClient(client){
	//new_client = document.getElementById('template_client_infobox').cloneNode(true)
	new_client =$("#template_client_infobox")
	new_client = new_client.html()
	//Replacing IDs
	new_client = new_client.replace("XXXX",client.mac)

	//Replacing Placeholders
	//new_client = new_client.replace("XXNAMEXX",client.name)
	new_client = new_client.replace("XXMACXX",client.mac)
	new_client = new_client.replace("XXIPXX",client.ip)
	new_client = new_client.replace("XXOSXX",client.os)
	//new_client.replace("XXUSAGEXX",client.usage) <- TODO

	c = document.getElementById('client_list')
	c.innerHTML += new_client

	//Remember to Refreshing Graph after adding

}

function refreshGraph(graph_id, datapoints,graphtype){
	//Refresh a graph with new datapoints
}



function setup(){
	//Setup
	//
}


//This schedules the getAllData to be ran every 5 sec.
var interval = window.setInterval(getAllData, 5000);

