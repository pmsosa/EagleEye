/// CONSTANTS ///
var getData_endpoint = "../getalldataset"	//This is the endpoint called to get information from flask
var startMon_endpoint = "../start_monitor"  //This is the endpoing called to start the monitoring process

var dataset = [] 	//This is the dataset object that will be acessed by getAllData
var colors = {'red':"#FF0000", 'black':"#000000",'yellow':'#FFFF00','blue':'#0000FF','green':'#008000'} //List of colors for our graphs
var chart_type = {'main':'usage'} //This dictionary specifies which type of graph we have set up initially for each chart.

/// FUNCTIONS ///

///TEMPORARY BULLSHIT
chartdata = {
	datasets: [{
	        label: 'Host 1',
	        data: [{ x: -10, y: 0 }, { x: 0, y: 10 }, { x: 10, y: 5 }],
	        fill: false,
	        borderColor: colors.red,
	        pointRadius: 3
	    	},
	    	{
	    	label: 'Host 2',
	        data: [{ x: -5, y: 0 }, { x: 1, y: 10 }, { x: 6, y: 5 }],
	        fill: false,
	        borderColor: colors.blue,
	        pointRadius: 1
	    	}
	    	]
}

options = {
	scales: {
		xAxes:[{
			type: 'time',
    		position: 'bottom',
			scaleLabel:{
				display:true,
				labelString:"Time"
			},
			time:{
				displayFormats:{
					millisecond: "h:mm:ss",
					second: "h:mm:ss",
					minute: "h:mm:ss",
					hour: "h:mm:ss"
				}
			}
		}],
		yAxes:[{
			scaleLabel:{
				display:true,
				labelString:"# of Packets"
			}
		}]
	},
	// scaleOverride: true,
    animation: false
}	


//Update the AP Bar to display the possible APs
function AP_update(data){
    var ap_bar = document.getElementById("setup_ap");
    for (i = 0; i < data.APs.length; i++){
        option = document.createElement("option");
        option.text = data.APs[i].name;
        ap_bar.add(option);
    }
    mode = "wait"
}

//Start monitoring (When user clicks on monitor button)
function start_monitor(){
    ap = document.getElementById("setup_ap")
    ap = ap.options[ap.selectedIndex].text
    pass = document.getElementById("setup_pass").value
    console.log("Start Monitoring on "+ap+" "+pass)

    monitor_info = {"bssid":ap,"password":pass}
    $.ajax(startMon_endpoint,{
        data: JSON.stringify(monitor_info),
        contentType: "application/json",
        type: "POST"
    });


    $("#setup_ap").prop('disabled',true)
    $("#setup_pass").prop('disabled',true)
    $("#setup_btn").prop('disabled',true)


    return false;
}

//Make chart areas visible for monitor mode
function prep_monitor_mode(){
    document.getElementById("total_container").style.display = "block";
    document.getElementById("client_header").style.display = "block";
    document.getElementById("AP_help").style.display = "none";
}


//Function call to get the the data from the ../getalldataset endpoint in flask
function getAllData(){
	$.get( getData_endpoint, function( data ) {
		console.log(data);

		//INIT MODE - Still not doing packet Capturing
		if (data.mode == "init"){
            //Avoid overfilling the dropdown for AP selection
            if (document.getElementById("setup_ap").options.length <= 1){
                AP_update(data);
            }
		}
        //MONITOR MODE - Capturing mode
		else{

          //If we are switching from AP select to monitor mode. Then make all graphs and spaces visible.
          if (dataset.mode != "mon"){
            prep_monitor_mode()
          }

          if (document.getElementById("setup_ap").options.length <= 1){
                AP_update(data);
                //TODO: Not that imporant, but perhaps fill the AP_select and AP_pass in
          }

		  //Check if we need to add any more clients to the website.
		  if ((dataset.clients == undefined) || (data.clients.length > dataset.clients.length)){
		  	n = 0
		  	if (dataset.clients != undefined){ n = dataset.clients.length}

		  	for (i = n; i < data.clients.length; i++){
				addClient(data.clients[i])
				//console.log("Created: "+data.clients[i].mac)	
		  	}

		  }

		  refreshClientGraphs(data)	//Refresh Client Graphs
		}


		dataset = data 	//Update Dataset
	});	
}


//Add a client to the front-end
function addClient(client){
	//new_client = document.getElementById('template_client_infobox').cloneNode(true)
	new_client =$("#template_client_infobox")
	new_client = new_client.html()
	//Replacing IDs
	while (new_client.search("XXXX") != -1){
		new_client = new_client.replace("XXXX",client.mac)
	}


	//Replacing Placeholders
	//new_client = new_client.replace("XXNAMEXX",client.name)
	new_client = new_client.replace("XXMACXX",client.mac)
	new_client = new_client.replace("XXIPXX",client.ip)
	new_client = new_client.replace("XXOSXX",client.os)
	//new_client.replace("XXUSAGEXX",client.usage) <- TODO

	c = document.getElementById('client_list')
	c.innerHTML += new_client

	chart_type[client.mac] = 0 //Initialize Chart Type
}


//Refresh The Client Maps
function refreshClientGraphs(data){
	clients = data.clients
	//Refresh a graph with new datapoints
  	for (i = 0; i < clients.length; i++){
  		
  		//Chart Type: 0 - Total Send/Recv usage
  		if (chart_type[clients[i].mac] == 0){ 

  			sentpoints = []
  			recvpoints = []

			for (j = 0; j < clients[i]["report"].length; j++){
				report = clients[i]["report"]
				//X-Axis
				time = new Date(report[j][0]*1000)
				//time = time.getHours()*100+ time.getMinutes()+(time.getSeconds()/100)
				//console.log(report)
				//Y-Axis
				sentpoints.push({x: time, y: report[j][1]["sent"]})
				recvpoints.push({x: time, y: report[j][1]["recv"]})
				//console.info(report)
			}

	  		chartdata = {
				datasets: [
							{label: 'Sent',
					        data: sentpoints,
					        fill: false,
					        borderColor: colors.red,
					        pointRadius: 3},

					    	{label: 'Recieved',
					        data: recvpoints,
					        fill: false,
					        borderColor: colors.blue,
					        pointRadius: 3}
				    	]
			}

			new Chart(clients[i].mac+"_chart", {
		    type: 'line',
		    data: chartdata,
		    options: options
			});
		}

		//Chart Type: 1 - UDP/TCP
		else if (chart_type[clients[i].mac] == 1){

			udppoints = []
			tcppoints = []

			for (j = 0; j < clients[i]["report"].length; j++){
				report = clients[i]["report"]
				//X-Axis
				time = new Date(report[j][0]*1000)
				//time = time.getHours()*100+ time.getMinutes()+(time.getSeconds()/100)
				//console.log(report)
				//Y-Axis
				udppoints.push({x: time, y: report[j][1]["udp"]})
				tcppoints.push({x: time, y: report[j][1]["tcp"]})
				//console.info(report)
			}

	  		chartdata = {
				datasets: [
							{label: 'UDP',
					        data: udppoints,
					        fill: false,
					        borderColor: colors.red,
					        pointRadius: 3},

					    	{label: 'TCP',
					        data: tcppoints,
					        fill: false,
					        borderColor: colors.blue,
					        pointRadius: 3}
				    	]
			}

						new Chart(clients[i].mac+"_chart", {
		    type: 'line',
		    data: chartdata,
		    options: options
			});
		}
		
		//Chart Type: 3 - Portwise Chart
		else if (chart_type[clients[i].mac] == 2){
			//DO THIS PORTWISE
			//PICK TOP PORTS, otherwise it'll be impossible to read.
		}

		//Chart Type: 4 - Portwise Chart
		else{
			//Some Default.
		}


	}
}

//Refresh the Main Graph
function refreshMainGraph(data){
    //TODO
}


//Run as soon as the website is loaded.
window.onload = function(){
    getAllData()
    //This schedules the getAllData to be ran every 5 sec.
    var interval = window.setInterval(getAllData, 5000);
}

