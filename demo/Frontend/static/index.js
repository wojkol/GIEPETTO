
        // Function to generate a new unique session ID
        function generateSessionId() {
            return 'sess-' + Math.random().toString(36).substr(2, 9); // Example format: sess-abc123xyz
        }

        // Initialize session_id with a new ID for each page load
        let session_id = generateSessionId();

       async function afterDocLoaded() {
            showSessions()
       }

       // function for changing session
        async function Changesession(id) {
            let chatBox = document.getElementById("chat-box");
            chatBox.innerHTML = ""            
            let new_id=""
            for(let i = 0;i<id.length-5;i++)
                new_id += id[i]
            console.log(`current session: ${new_id}`)
            session_id = new_id

            //request for history data
            let response = await fetch("/api/loadFormatedSessions/", {
                method: "POST",  // Ensure this is POST, not GET
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: new_id})
            });
            let data = await response.json()

            //newfunction
            for(let i = 0;i<data.ChatHistory.length;i++){
                let odp = document.createElement("p")
                odp.innerHTML = marked.parse(data.ChatHistory[i])
                chatBox.appendChild(odp)
                chatBox.appendChild(document.createElement("br"))
            }

           
            //old function
            //data.ChatHistory =  marked.parse(data.ChatHistory)
            //chatBox.innerHTML=data.ChatHistory;


        }
        //function for showin session options in GUI
        async function showSessions(existing = false){
            document.getElementById("leftMENU").innerHTML="<p>Sesje:</p>"
            let response = await fetch("/api/sessions/", {
                method: "POST",  // Ensure this is POST, not GET
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: "test"})
            });
            let data = await response.json()
            
            if(existing==false){
                for(let i = 0;i<data.sessionNames.length;i++){
                    sessionName =  document.createElement("a");
                    for(let x = 0;x<data.sessionNames[i].length-5;x++){
                        sessionName.innerHTML += data.sessionNames[i][x]
                    }
                    //sessionName.innerHTML = data.sessionNames[i];
                    sessionName.setAttribute("onclick",`Changesession("${sessionName.innerHTML+".json"}")`)

                    document.getElementById("leftMENU").appendChild(sessionName);
                    document.getElementById("leftMENU").appendChild(document.createElement("br"))
                }
            }
            else{
                sessionName =  document.createElement("a");
                sessionName.innerHTML = data.sessionNames[data.sessionNames.length-1];
                document.getElementById("leftMENU").appendChild(sessionName);
                document.getElementById("leftMENU").appendChild(document.createElement("br"))
            }
            
            
        }


        async function  newConversation() {
            let chatBox = document.getElementById("chat-box");
            session_id = generateSessionId();
            chatBox.innerHTML = "";
            showSessions();

        }
      



        //propper chat function
        async function sendMessage() {
            let userInput = document.getElementById("user-input").value;
            if (!userInput.trim()) return;

            // Display user message
            let chatBox = document.getElementById("chat-box");

            odp1 = document.createElement("p")
            odp1.innerHTML = `<strong>You:</strong> ${userInput}`
            chatBox.appendChild(odp1)
            document.getElementById("user-input").value = "";

            // Send message to Django backend (Make sure it's POST)
            let response = await fetch("/api/chat/", {
                method: "POST",  // Ensure this is POST, not GET
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userInput, session_id: session_id })
            });

            let data = await response.json();
            session_id = data.session_id;  // Store session ID for continuity
            // You can choose whether to store session_id in localStorage or just in the session

            // Display AI response
            odp2 = document.createElement("p");
            data.ai_message =  marked.parse(data.ai_message)
            odp2.innerHTML=`<strong>AI:</strong>${data.ai_message}`;
            chatBox.appendChild(odp2);
        }