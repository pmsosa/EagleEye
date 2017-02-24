/// CONSTANTS ///
var getData_endpoint = "../getalldataset"	//This is the endpoint called to get information from flask
var startMon_endpoint = "../start_monitor"  //This is the endpoing called to start the monitoring process

var dataset = [] 	//This is the dataset object that will be acessed by getAllData
var colors = {'red':"#FF0000", 'black':"#000000",'yellow':'#FFFF00','blue':'#0000FF','green':'#008000'} //List of colors for our graphs
var chart_type = {'main':0} //This dictionary specifies which type of graph we have set up initially for each chart.
var charts = {"main": null}
var timestep = 5
/// FUNCTIONS ///

///Options for the Charts
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
        option.text = data.APs[i].essid;
        ap_bar.add(option);
    }
    mode = "wait"
}

//Update The WiFi Table
function refreshMainTable(data){
    document.getElementById("ap_name").innerHTML = data.monitor_info.essid;
    document.getElementById("ap_usage").innerHTML = "TODO"
    document.getElementById("ap_mac").innerHTML = data.monitor_info.mac;
    document.getElementById("ap_channel").innerHTML = data.monitor_info.channel;
}

//Start monitoring (When user clicks on monitor button)
function start_monitor(){
    ap = document.getElementById("setup_ap")
    ap = ap.options[ap.selectedIndex].text
    pass = document.getElementById("setup_pass").value
    console.log("Start Monitoring on "+ap+" "+pass)

    monitor_info = {"essid":ap,"password":pass}
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
function prep_monitor_mode(data){
    document.getElementById("total_container").style.display = "block";
    document.getElementById("client_header").style.display = "block";
    document.getElementById("AP_help").style.display = "none";

    $("#setup_ap").prop('disabled',true)
    $("#setup_pass").prop('disabled',true)
    $("#setup_btn").prop('disabled',true)

    //Fill the AP and Password Bar
    var ap_bar = document.getElementById("setup_ap");
    option = document.createElement("option");
    option.text = data.monitor_info.essid;
    option.selected = true;
    ap_bar.add(option);
    document.getElementById("setup_pass").value = data.monitor_info.password;

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
            prep_monitor_mode(data)
            refreshMainTable(data)
          }

          //Update the list of APs in case it hasn;t already been updated
          if (document.getElementById("setup_ap").options.length <= 1){
                AP_update(data);
                //TODO: Not that imporant, but perhaps fill the AP_select and AP_pass in
          }

		  //Check if we need to add any more clients to the website.
		  if ((dataset.clients == undefined) || (data.clients.length > dataset.clients.length)){
		  	n = 0
		  	if (dataset.clients != undefined){ n = dataset.clients.length}

		  	for (i = n; i < data.clients.length; i++){
                if (data.clients[i].mac != data.monitor_info.mac){ //Don't Add The AP
    				addClient(data.clients[i])
    				//console.log("Created: "+data.clients[i].mac)	
                }
		  	}

		  }

          refreshClientInfo(data)   //Refresh Client Info (Leaks Usage, etc..)
		  refreshClientGraphs(data)	//Refresh Client Graphs
          refreshMainGraph(data)    //Refresh Main Graph
		}


		dataset = data 	//Update Dataset
	});	
}


//Refresh the client information (usage, leaks, etc.)
function refreshClientInfo(data){
    for (j = 0; j < data.clients.length; j++){
        c = document.getElementById(data.clients[j].mac+"_leaks");
        if (data.clients[j].leak.length == 0){ c.innerHTML = "None"}
        else{c.innerHTML = "⚠️️ Leaks found ("+data.clients[j].leak.length+")"}
    }

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
            //console.log
            //console.log("Here "+data.timesteps[0]+5+" - "+data.timesteps[data.timesteps.length-1]+5)
            for (k = data.timesteps[0]+timestep; k < data.timesteps[data.timesteps.length-1]+timestep; k=k+timestep){
                //console.log(k)
                ys = 0;
                yr = 0;
                
                for (j = 0; j < clients[i]["report"].length; j++){
    				//if (clients[i]["mac"] != ap_essid){
                        report = clients[i]["report"]
        				//X-Axis
        				//time = new Date(report[j][0]*1000)

        				//Y-Axis
                        if (report[j][0] > k-timestep &&  report[j][0] <= k){
                            ys += report[j][1]["sent"]
                            yr += report[j][1]["recv"]
                        }
                        else if (report[j][0] > k){
                            break;
                        }
    			}

                sentpoints.push({x: k*1000, y: ys})
                recvpoints.push({x: k*1000, y: yr})
                //console.log(sentpoints)

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

            //Destroy the Previous Chart
            try{charts[clients[i].mac].destroy()}
            catch(err){/*Don't Worry be Happy*/}

			charts[clients[i].mac] = new Chart(clients[i].mac+"_chart", {
		    type: 'line',
		    data: chartdata,
		    options: options
			});
		}

		//Chart Type: 1 - UDP/TCP
		else if (chart_type[clients[i].mac] == 1){

			udppoints = []
			tcppoints = []

             for (k = data.timesteps[0]+timestep; k < data.timesteps[data.timesteps.length-1]+timestep; k=k+timestep){
                
                yu = 0;
                yt = 0;
                
                for (j = 0; j < clients[i]["report"].length; j++){
                    //if (clients[i]["mac"] != ap_essid){
                        report = clients[i]["report"]
                        //X-Axis
                        //time = new Date(report[j][0]*1000)

                        //Y-Axis
                        if (report[j][0] > k-timestep && report[j][0] <= k){
                            yu += report[j][1]["udp"]
                            yt += report[j][1]["tcp"]
                        }
                        else if (report[j][0] > k){
                            break;
                        }
                }

                udppoints.push({x: k*1000, y: yu})
                tcppoints.push({x: k*1000, y: yt})

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

            //Destroy the Previous Chart
            try{charts[clients[i].mac].destroy()}
            catch(err){/*Don't Worry be Happy*/}


			charts[clients[i].mac] = new Chart(clients[i].mac+"_chart", {
		    type: 'line',
		    data: chartdata,
		    options: options
			});
		}
		
		//Chart Type: 3 - Portwise Chart
		else if (chart_type[clients[i].mac] == 2){
		    //DO THIS PORTWISE
		    //PICK TOP PORTS, otherwise it'll be impossible to read.
		    httpspoints = []
		    httppoints = []
		    otherpoints = []
		    /*for(m = 0; m < clients[i]["report"].length; m++) {
			report = clients[i]["report"]
			
		    }*/
		    for (k = data.timesteps[0]+timestep; k < data.timesteps[data.timesteps.length-1]+timestep; k=k+timestep){
			
			ys = 0;
			yh = 0;
			yo = 0;
			for (j = 0; j < clients[i]["report"].length; j++){
			    //if (clients[i]["mac"] != ap_essid){
                            report = clients[i]["report"]
                            //X-Axis
                            //time = new Date(report[j][0]*1000)

                            //Y-Axis
                            if (report[j][0] > k-timestep && report[j][0] <= k){
				//if(!(report[j][1]["ports"]["443"] === undefined)) {
				ys += report[j][1]["ports"]["443"]
				
				//}
				//if(!(report[j][1]["ports"]["80"] === undefined)) {
				    yh += report[j][1]["ports"]["80"]
				//}
				count = 0;
				for(key in report[j][1]["ports"]) {
				    if(key != "443" && key  != "80") {
					count += report[j][1]["ports"][key]
				    }
				}
				yo += count
				//ys += count
				//yh += count
                            }
                            else if (report[j][0] > k){
				break;
                            }
			}

			httpspoints.push({x: k*1000, y: ys})
			httppoints.push({x: k*1000, y: yh})
			otherpoints.push({x: k*1000, y: yo})

		    }

	  	    chartdata = {
			datasets: [
			    {label: 'HTTPS',
			     data: httpspoints,
			     fill: false,
			     borderColor: colors.red,
			     pointRadius: 3},
			    
			    {label: 'HTTP',
			     data: httppoints,
			     fill: false,
			     borderColor: colors.blue,
			     pointRadius: 3},

			    {label: 'Other',
			     data: otherpoints,
			     fill: false,
			     borderColor: colors.green,
			     pointRadius: 3}
			]
		    }
		    try{charts[clients[i].mac].destroy()}
		    catch(err){/*Don't Worry be Happy*/}


		    charts[clients[i].mac] = new Chart(clients[i].mac+"_chart", {
		    type: 'line',
		    data: chartdata,
		    options: options
		    });
		}
	   

		//Chart Type: 4 - Portwise Chart
		else{
			//Some Default.
		}


	}
}

//Button binding function to switch type of graph.
function switch_graph(mac,type){
    chart_type[mac] = type;
    document.getElementById(mac+"_toggle_"+0).disabled = false;
    document.getElementById(mac+"_toggle_"+1).disabled = false;
    document.getElementById(mac+"_toggle_"+2).disabled = false;

    document.getElementById(mac+"_toggle_"+type).disabled = true;
}


//Refresh the Main Graph
function refreshMainGraph(data){

    
    if (chart_type["main"] == 0){ 

        //Destroy the Previous Chart
        try{charts["main"].destroy()}
        catch(err){/*Don't Worry be Happy*/}

        sentpoints = []
        recvpoints = []

        //Highly unscalable. But its late and I just want this to work.
        for (k = data.timesteps[0]+timestep; k < data.timesteps[data.timesteps.length-1]+timestep; k=k+timestep){
            
            ys = 0;
            yr = 0;

            //if (fff){console.log("k'--"+k)}
            for (i = 0; i < data.clients.length;i++){
                for (j = 0; j < data.clients[i].report.length;j++){

                    if (data.clients[i].report[j][0] > k-timestep && data.clients[i].report[j][0] <= k){
                        ys += data.clients[i].report[j][1]["sent"]
                        yr += data.clients[i].report[j][1]["recv"]
                        //if (fff){console.log(ys+"-"+data.clients[i].report[j][1]["sent"]+" <"+i+","+j+">")}
                    }
                    else if (data.clients[i].report[j][0] > k){
                        break; //Go to next client and don't waste your time.
                    }
                }

            }

            sentpoints.push({x: k*1000, y: ys})
            recvpoints.push({x: k*1000, y: yr})
            fff = false
                    
        }

        //console.info(sentpoints)
        //console.info(recvpoints)

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


        charts["main"] = new Chart("mainChart", {
            type: 'line',
            data: chartdata,
            options: options
        });


    }
}


//Run as soon as the website is loaded.
window.onload = function(){
    getAllData()
    //This schedules the getAllData to be ran every 5 sec.
    var interval = window.setInterval(getAllData, 5000);
}

