
  var wsUri;
  var consoleLog;
  var connectBut;
  var disconnectBut;
  var sendMessage;
  var sendBut;
  var clearLogBut;

  function echoHandlePageLoad()
  {
    if (window.WebSocket)
    {
      document.getElementById("webSocketSupp").style.display = "block";
    }
    else
    {
      document.getElementById("noWebSocketSupp").style.display = "block";
    }

    wsUri = document.getElementById("wsUri");

    connectBut = document.getElementById("connect");
    connectBut.onclick = doConnect;

    disconnectBut = document.getElementById("disconnect");
    disconnectBut.onclick = doDisconnect;

    sendMessage1 = document.getElementById("sendMessage1");
	sendMessage2 = document.getElementById("sendMessage2");
	sendMessage3 = document.getElementById("sendMessage3");

    sendBut1 = document.getElementById("send1");
    sendBut1.onclick = doSend1;
	sendBut2 = document.getElementById("send2");
    sendBut2.onclick = doSend2;
	sendBut3 = document.getElementById("send3");
    sendBut3.onclick = doSend3;

    consoleLog = document.getElementById("consoleLog");

    clearLogBut = document.getElementById("clearLogBut");
    clearLogBut.onclick = clearLog;

    setGuiConnected(false);

    document.getElementById("disconnect").onclick = doDisconnect;
    document.getElementById("send1").onclick = doSend1;
	document.getElementById("send2").onclick = doSend2;
	document.getElementById("send3").onclick = doSend3;
  }


  function doConnect()
  {
		if (!window.WebSocket)
    {
			logToConsole('<span style="color: red;"><strong>Error:</strong> This browser does not have support for WebSocket</span>');
			return;
		}
    websocket = new WebSocket(wsUri.value);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
  }

  function doDisconnect()
  {
    websocket.close()
  }

  function doSend1()
  {
	d = new Date()
	msg = sendMessage1.value
	msg = msg.replace("HOUR", d.getTime());
    logToConsole("SENT: " + msg);
    websocket.send(msg);
  }
  
  function doSend2()
  {
	d = new Date()
	msg = sendMessage2.value
	msg = msg.replace("HOUR", d.getTime());
    logToConsole("SENT: " + msg);
    websocket.send(msg);
  }
  
  function doSend3()
  {
	d = new Date()
	msg = sendMessage3.value
	msg = msg.replace("HOUR", d.getTime());
    logToConsole("SENT: " + msg);
    websocket.send(msg);
  }

  function logToConsole(message)
  {
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;
    consoleLog.appendChild(pre);

    while (consoleLog.childNodes.length > 50)
    {
      consoleLog.removeChild(consoleLog.firstChild);
    }

    consoleLog.scrollTop = consoleLog.scrollHeight;
  }

  function onOpen(evt)
  {
    logToConsole("CONNECTED");
    setGuiConnected(true);
  }

  function onClose(evt)
  {
    logToConsole("DISCONNECTED");
    setGuiConnected(false);
  }

  function onMessage(evt)
  {
    logToConsole('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
  }

  function onError(evt)
  {
    logToConsole('<span style="color: red;">ERROR:</span> ' + evt.data);
  }

  function setGuiConnected(isConnected)
  {
    wsUri.disabled = isConnected;
    connectBut.disabled = isConnected;
    disconnectBut.disabled = !isConnected;
    sendMessage1.disabled = !isConnected;
    sendBut1.disabled = !isConnected;
	sendMessage2.disabled = !isConnected;
    sendBut2.disabled = !isConnected;
	sendMessage3.disabled = !isConnected;
    sendBut3.disabled = !isConnected;
    var labelColor = "black";
    if (isConnected)
    {
      labelColor = "#999999";
    }

  }

	function clearLog()
	{
		while (consoleLog.childNodes.length > 0)
		{
			consoleLog.removeChild(consoleLog.lastChild);
		}
	}



  window.addEventListener("load", echoHandlePageLoad, false);
