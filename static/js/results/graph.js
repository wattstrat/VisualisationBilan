class DefaultVirtualGraph{
    constructor(parameters, simus, geocodes, precision, start, end, graphType, batiments=false, aggrterr=false, territories=null, aggrgeocode=false, download=false){
	this._params = parameters;
	this._simus = simus;
	this._geocodes = geocodes;
	this._precision = precision;
	this._start = start;
	this._end = end;
	this._download = download;
	this._graphType = graphType;
	this._batiments=batiments;
	this._territories = territories;
	this._aggrgeocode = aggrgeocode;
	// Include les sommes sur les territoires
	this._aggrterr=aggrterr;
    }

    randomUUID() {
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
	    var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
	    return v.toString(16);
	});
    }

    _getVariableNode(simu, pathDB, varname, label, geocodes, start, end, precision){
	return     {
	    'attrs': {
		'SRDConfig': {
		    'simulation': simu,
		    'pathDB': pathDB,
		    'varname': varname,
		    'label': label,
		    'geocodes': geocodes,
		    'begin': start,
		    'end': end,
		    'precision': precision,
		}
	    },
	    'id': this.randomUUID(),
	    'outPorts': ['out'],
	    'inPorts': [],
	    'type': 'WS.Variable.ByYear'
	}
    }

    getVariableNode(simu, pathDB, varname){
	var fun = function(el) {
	    if (el["geocode"].toLowerCase().startsWith('group_')){
		return el["sub"].concat([el["geocode"]]);
	    }
	    else{
		return el["geocode"];
	    }
	};
	var nodes=[];
	
	if(!this._download && this._graphType == "map"){
	    // map => get include element
	    fun = function(el) {
		return el["sub"].concat([el["geocode"]])
	    };
	}

	var geocodes=_.flatten(_.map(this._geocodes, fun), true)
	var start=this._start;
	var end= this._end.replace("T00:", "T23:");

	if(varname["_type"] == 0){
	    var node=this._getVariableNode(simu, pathDB, varname["name"], varname["label"], geocodes, start, end,this._precision);
	    nodes.push(node);
	    return {'last': node, 'nodes': nodes}
	}
	else{
	    var inputs = [];
	    var nNodes = varname["includes"].length;
	    for(var i = 0; i< nNodes; i++){
		var input="in-" + i;
		inputs.push(input);
	    }
	    var sumNode = {
		'attrs': {
		    'SRDConfig': {
			'varname': varname["name"],
			'label': varname["label"],
			'shortLabel': varname["label"],
			'field': varname["name"]
		    }
		},
		'id': this.randomUUID(),
		'outPorts': ['out'],
		'inPorts': inputs,
		'type': 'WS.Utils.AggregateInputs'
	    }
	    nodes.push(sumNode);
	    
	    for(var i = 0; i< nNodes; i++){
		var iVarName = varname["includes"][i];
		var input="in-" + i;
		var node = this._getVariableNode(simu, pathDB, iVarName["varname"], iVarName["label"], geocodes, start, end,this._precision);
		nodes.push(node);
		nodes.push(this.addLink(node.id, 'out', sumNode.id, input));
	    }
	    return {'last': sumNode, 'nodes': nodes}
	}
    }
    getBatimentVariableNode() {
	return {
            'attrs': {
		'SRDConfig': {
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type': 'WS.Variable.Batiment'
	}
    }

    getSplitVariableByGeocodeNode() {
	if(this._download){
	    var SplitFilter = "WS.SplitFilter.DictMetaDataAddVar";
	}
	else{
	    var SplitFilter = "WS.SplitFilter.DictMetaDataChangeVar";
	}
	if(this._simus.length > 1){
	    SplitFilter += "MultipleSimu";
	}
	
	return {
            'attrs': {
		'SRDConfig': {
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type': SplitFilter
	}
    }
    getRenameVariableBySimuNode() {
	return {
            'attrs': {
		'SRDConfig': {
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type':  "WS.Utils.RenameFilterWithSimulation"
	}
    }
    getLinerise(){
	return {
            'attrs': {
		'SRDConfig': {
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type': "WS.Utils.LineriseFilterTimely"
	}
    }
    getSummationTerritoryNode(){
	return {
            'attrs': {
		'SRDConfig': {
		    'replace': !this._download,
		    'territories': this._territories,
		    
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type': 'WS.Utils.AggregateTerritory'
	}

    }
    getSummationGeocodeNode(){
	return {
            'attrs': {
		'SRDConfig': {
		}
            },
            'id': this.randomUUID(),
            'outPorts': ['out'],
            'inPorts': ['in'],
            'type': 'WS.Utils.AggregateGeocode'
	}

    }

    getTransformForVariable(simu, pathDB, varname){
	var ret = this.getVariableNode(simu, pathDB, varname)
	var nodes = ret["nodes"];
	var curNode = ret["last"];

	if (this._graphType == "map" && this._batiments){
	    // we are not a map => split by geocodes
	    var bati = this.getBatimentVariableNode();
	    nodes.push(bati);
	    nodes.push(this.addLink(curNode.id, 'out', bati.id, 'in'));
	    curNode = bati;
	}
	
	if (this._graphType != "map" || this._download){
	    if(this._aggrterr) {
		var aggrterr = this.getSummationTerritoryNode();
		nodes.push(aggrterr);
		nodes.push(this.addLink(curNode.id, 'out', aggrterr.id, 'in'));
		curNode = aggrterr;
	    }
	    else if(this._aggrgeocode){
		var aggrgeocode = this.getSummationGeocodeNode();
		nodes.push(aggrgeocode);
		nodes.push(this.addLink(curNode.id, 'out', aggrgeocode.id, 'in'));
		curNode = aggrgeocode;
	    }
	    if(!this._aggrgeocode){
		// we are not a map => split by geocodes
		var split = this.getSplitVariableByGeocodeNode();
		nodes.push(split);
		nodes.push(this.addLink(curNode.id, 'out', split.id, 'in'));
		curNode = split;
	    }
	}
	if (this._simus.length > 1){
	    var rename = this.getRenameVariableBySimuNode();
	    nodes.push(rename);
	    nodes.push(this.addLink(curNode.id, 'out', rename.id, 'in'));
	    curNode = rename;
	    // Transform label / varname with simu name
	}
	// Linerise filter to get one big list
	var linerise = this.getLinerise();
	nodes.push(linerise);
	nodes.push(this.addLink(curNode.id, 'out', linerise.id, 'in'));
	curNode = linerise;
	return {'last': curNode, 'nodes': nodes}
    }

    getProviderNode(nInputs){
	var inputs = []
	for(var i = 0; i< nInputs; i++){
	    var input="in-" + i;
	    inputs.push(input);
	}
	var res = {
            'attrs': {
		'SRDConfig': {
		    'axis': true,
		}
            },
            'id': this.randomUUID(),
            'outPorts': [],
            'inPorts': inputs
	}
	if (this._download){
	    // For now, download as CSV
	    //res['type'] = "WS.Provider.CSV";
	    // For now, download as XLSX
	    res['type'] = "WS.Provider.XLSX";

	    res['attrs']['SRDConfig']['filename'] = 'results';
	}
	else{
	    // a graphic
	    res['type'] =  "WS.Provider.Graphic." + this._graphType;
	}
	return res;
    }

    getAllNodes(){
	//initialise VariableFetcher with correct treatment
	var nodes = [];
	var lastNodes = [];
	for(var vID = 0; vID < this._params.length; vID++){
	    for(var sID = 0; sID < this._simus.length; sID++){
		var ret = this.getTransformForVariable(
		    this._simus[sID], "default",
		    this._params[vID],
		);
		nodes = nodes.concat(ret["nodes"]);
		lastNodes.push(ret["last"]);
	    }
	}

	// inititalise Provider
	var providerNode = this.getProviderNode(lastNodes.length);
	nodes.push(providerNode);
	for(var i = 0; i< lastNodes.length; i++){
	    var input="in-" + i;
	    nodes.push(this.addLink(lastNodes[i].id, 'out', providerNode.id, input));
	}
	self._nodes = nodes
	return nodes;
    }

    addLink(sUUID, sPort, tUUID, tPort){
	return {
	    'id': this.randomUUID(),
	    'source': {
		'port': sPort,
		'id': sUUID
	    },
	    'target': {
		'port': tPort,
		'id': tUUID
	    },
	    'type': 'devs.Link',
	};
    }

    json() {
	//return JSON string
	//return JSON.stringify(this.getAllNodes());
	//return JSON
	return this.getAllNodes();
    }
}

